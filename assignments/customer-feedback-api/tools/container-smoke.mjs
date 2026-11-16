import assert from 'node:assert/strict';
const url = process.env.API_URL ?? 'http://127.0.0.1:18080';
const key = process.env.READ_API_KEY;
if (!key) throw new Error('Provide the container test read key through READ_API_KEY');
let ready = false;
for (let attempt = 0; attempt < 40; attempt++) {
  try { if ((await fetch(`${url}/health`)).ok) { ready = true; break; } } catch { /* wait for listener */ }
  await new Promise((resolve) => setTimeout(resolve, 500));
}
assert.ok(ready, 'container became healthy');
const input = { name: 'Anita', email: 'anita@example.com', rating: 5, comment: 'Excellent product' };
const created = await fetch(`${url}/feedback`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(input) });
assert.equal(created.status, 201); assert.deepEqual(await created.json(), { id: 1, ...input });
assert.equal((await fetch(`${url}/feedback`)).status, 401);
const records = await fetch(`${url}/feedback`, { headers: { 'X-API-Key': key } }); assert.equal(records.status, 200); assert.equal((await records.json()).length, 1);
const single = await fetch(`${url}/feedback/1`, { headers: { 'X-API-Key': key } }); assert.equal(single.status, 200); assert.deepEqual(await single.json(), { id: 1, ...input });
assert.equal((await fetch(`${url}/feedback/999`, { headers: { 'X-API-Key': key } })).status, 404);
assert.equal((await fetch(`${url}/feedback`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ...input, rating: 0 }) })).status, 400);
console.log('PASS: live container health, create, authenticated list/ID reads, missing ID and invalid input.');
