import test from 'node:test';
import assert from 'node:assert/strict';
import { validateFeedback } from '../src/validation.js';

const valid = { name: 'Anita', email: 'anita@example.com', rating: 5, comment: 'Excellent product' };
test('valid feedback is accepted', () => assert.equal(validateFeedback(valid).errors.length, 0));
test('whitespace-only name is rejected', () => assert.ok(validateFeedback({ ...valid, name: '   ' }).errors.length));
test('email must contain a domain and suffix', () => assert.ok(validateFeedback({ ...valid, email: 'a@' }).errors.length));
test('rating strings are not coerced to numbers', () => assert.ok(validateFeedback({ ...valid, rating: '5' }).errors.length));
test('fractional ratings are rejected', () => assert.ok(validateFeedback({ ...valid, rating: 1.5 }).errors.length));
test('whitespace-only comment is rejected', () => assert.ok(validateFeedback({ ...valid, comment: '\t\n' }).errors.length));
test('strings are normalized', () => assert.deepEqual(validateFeedback({ ...valid, name: ' Anita ', comment: ' Great ' }).value, { ...valid, name: 'Anita', comment: 'Great' }));

for (const field of ['name', 'email', 'rating', 'comment']) {
  test(`missing ${field} is rejected`, () => { const body = { ...valid }; delete body[field]; assert.ok(validateFeedback(body).errors.length); });
}
for (const body of [null, undefined, [], 'text', 123, true]) {
  test(`nonobject body ${JSON.stringify(body)} is rejected`, () => assert.ok(validateFeedback(body).errors.length));
}
for (const rating of [0, -1, 6, 1.2, NaN, Infinity, null, true, '1']) {
  test(`invalid rating ${String(rating)} is rejected`, () => assert.ok(validateFeedback({ ...valid, rating }).errors.length));
}
for (const rating of [1, 5]) test(`rating boundary ${rating} is valid`, () => assert.equal(validateFeedback({ ...valid, rating }).errors.length, 0));
for (const [field, value] of [['name', 1], ['comment', {}], ['email', null], ['name', 'x'.repeat(101)], ['comment', 'x'.repeat(2001)], ['email', 'x'.repeat(255)]]) {
  test(`invalid ${field} type or length rejected: ${typeof value}`, () => assert.ok(validateFeedback({ ...valid, [field]: value }).errors.length));
}
test('maximum name/comment boundaries accepted', () => assert.equal(validateFeedback({ ...valid, name: 'x'.repeat(100), comment: 'x'.repeat(2000) }).errors.length, 0));
test('unknown and prototype-related keys are rejected', () => {
  const body = JSON.parse('{"name":"Anita","email":"a@b.com","rating":5,"comment":"Great","__proto__":{"admin":true}}');
  assert.ok(validateFeedback(body).errors.length); assert.equal({}.admin, undefined);
});
test('unicode name and comment are supported', () => assert.equal(validateFeedback({ ...valid, name: 'Жан', comment: 'Рақмет!' }).errors.length, 0));
test('validation never modifies input', () => { const body = { ...valid, name: ' Anita ' }; validateFeedback(body); assert.equal(body.name, ' Anita '); });
