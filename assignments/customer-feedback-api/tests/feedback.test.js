import test from 'node:test';
import assert from 'node:assert/strict';
import request from 'supertest';
import { createApp } from '../src/app.js';
import { createFeedbackStore, CapacityError } from '../src/feedback.js';
import { parseFeedbackId } from '../src/validation.js';

const feedback = { name: 'Anita', email: 'anita@example.com', rating: 5, comment: 'Excellent product' };
const app = (options = {}) => createApp({ production: false, readApiKey: undefined, ...options });

test('empty collection returns 200 and an array', async () => { const response = await request(app()).get('/feedback').expect(200); assert.deepEqual(response.body, []); });
test('POST returns 201, exact record and Location header', async () => {
  const response = await request(app()).post('/feedback').send(feedback).expect(201);
  assert.deepEqual(response.body, { id: 1, ...feedback }); assert.equal(response.headers.location, '/feedback/1');
});
test('GET collection and GET ID return the created record', async () => {
  const api = app(); const created = await request(api).post('/feedback').send(feedback).expect(201);
  const list = await request(api).get('/feedback').expect(200); assert.deepEqual(list.body, [created.body]);
  const single = await request(api).get('/feedback/1').expect(200); assert.deepEqual(single.body, created.body);
});
test('unknown numeric ID returns 404', async () => { await request(app()).get('/feedback/999').expect(404); });
for (const id of ['0', '-1', 'abc', '1.5', '01', '9007199254740992']) {
  test(`invalid ID ${id} returns 400`, async () => { await request(app()).get(`/feedback/${id}`).expect(400); });
}
test('malformed JSON returns a sanitized 400', async () => {
  const response = await request(app()).post('/feedback').type('json').send('{bad').expect(400);
  assert.equal(response.body.error.code, 'INVALID_JSON_OR_URI'); assert.equal(JSON.stringify(response.body).includes('SyntaxError'), false);
});
test('missing body returns 400', async () => { await request(app()).post('/feedback').expect(400); });
test('unsupported body encoding cannot bypass validation', async () => { await request(app()).post('/feedback').type('text').send('name=test').expect(400); });
test('array body rejected over HTTP', async () => { await request(app()).post('/feedback').send([]).expect(400); });
test('invalid input is not persisted and does not consume an ID', async () => {
  const api = app(); await request(api).post('/feedback').send({ ...feedback, rating: 0 }).expect(400);
  const good = await request(api).post('/feedback').send(feedback).expect(201); assert.equal(good.body.id, 1);
  const list = await request(api).get('/feedback').expect(200); assert.equal(list.body.length, 1);
});
test('normalization is visible in HTTP response', async () => {
  const response = await request(app()).post('/feedback').send({ ...feedback, name: ' Anita ', comment: ' Great ' }).expect(201);
  assert.equal(response.body.name, 'Anita'); assert.equal(response.body.comment, 'Great');
});
test('20 concurrent creates have unique sequential IDs', async () => {
  const api = app(); const responses = await Promise.all(Array.from({ length: 20 }, () => request(api).post('/feedback').send(feedback).expect(201)));
  assert.deepEqual(responses.map((r) => r.body.id).sort((a, b) => a - b), Array.from({ length: 20 }, (_, i) => i + 1));
});
test('app instances isolate storage', async () => {
  await request(app()).post('/feedback').send(feedback).expect(201); const response = await request(app()).get('/feedback').expect(200); assert.deepEqual(response.body, []);
});
test('storage returns defensive copies', () => {
  const store = createFeedbackStore(); const created = store.create(feedback); created.name = 'changed';
  const list = store.list(); list[0].email = 'changed'; const single = store.find(1); single.comment = 'changed';
  assert.deepEqual(store.find(1), { id: 1, ...feedback }); assert.equal(store.find(99), undefined);
});
test('storage is deliberately ephemeral', () => { const store = createFeedbackStore(); store.create(feedback); assert.deepEqual(createFeedbackStore().list(), []); });
test('bounded storage rejects additional creates', () => {
  const store = createFeedbackStore({ maxRecords: 1 }); store.create(feedback); assert.throws(() => store.create(feedback), CapacityError);
  assert.throws(() => createFeedbackStore({ maxRecords: 0 }), RangeError);
});
test('capacity exhaustion becomes 503 without stack leakage', async () => {
  const api = app({ store: createFeedbackStore({ maxRecords: 1 }) });
  await request(api).post('/feedback').send(feedback).expect(201); const response = await request(api).post('/feedback').send(feedback).expect(503);
  assert.equal(response.body.error.code, 'CAPACITY_REACHED'); assert.equal(response.body.stack, undefined);
});
test('oversized JSON body returns 413', async () => { await request(app()).post('/feedback').send({ ...feedback, comment: 'x'.repeat(20_000) }).expect(413); });
test('request IDs and security headers are supplied', async () => {
  const response = await request(app()).get('/health').expect(200);
  assert.match(response.headers['x-request-id'], /^[0-9a-f-]{36}$/); assert.equal(response.headers['x-content-type-options'], 'nosniff'); assert.equal(response.headers['x-powered-by'], undefined);
});
test('unrecognized route returns JSON 404', async () => { const response = await request(app()).get('/unknown').expect(404); assert.equal(response.body.error.code, 'NOT_FOUND'); });
test('server faults are sanitized in responses and logs', async () => {
  const events = []; const api = app({ store: { list() { throw new Error('secret-internal-details'); } }, logger: { error: (event) => events.push(event) } });
  const response = await request(api).get('/feedback').expect(500); assert.equal(response.body.error.code, 'INTERNAL_ERROR');
  assert.ok(!JSON.stringify([response.body, events]).includes('secret-internal-details'));
});
test('production startup fails closed without a sufficiently long read key', () => {
  assert.throws(() => createApp({ production: true, readApiKey: '' }), /READ_API_KEY/);
  assert.throws(() => createApp({ production: true, readApiKey: 'short' }), /READ_API_KEY/);
});
test('configured read key protects collection, ID and HEAD without blocking POST', async () => {
  const key = 'test-only-key-at-least-24-characters'; const api = app({ production: true, readApiKey: key });
  await request(api).post('/feedback').send(feedback).expect(201);
  await request(api).get('/feedback').expect(401); await request(api).get('/feedback/1').set('X-API-Key', 'wrong').expect(401);
  await request(api).head('/feedback').expect(401);
  const response = await request(api).get('/feedback').set('X-API-Key', key).expect(200); assert.equal(response.body.length, 1);
});
test('rate limiting returns 429 and ignores spoofed forwarding headers', async () => {
  const api = app({ rateLimitMax: 2 }); await request(api).get('/feedback').set('X-Forwarded-For', '192.0.2.1').expect(200);
  await request(api).get('/feedback').set('X-Forwarded-For', '192.0.2.2').expect(200);
  await request(api).get('/feedback').set('X-Forwarded-For', '192.0.2.3').expect(429);
  await request(api).get('/health').expect(200);
});
test('strict ID parser rejects unsafe and ambiguous values', () => { assert.equal(parseFeedbackId('1'), 1); for (const value of [null, '1e2', '+1', ' 1', '0x10']) assert.equal(parseFeedbackId(value), null); });
