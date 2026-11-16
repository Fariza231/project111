/** Reproduces the actual red-stage defects without changing production imports. */
import test from 'node:test';
import assert from 'node:assert/strict';
import { validateFeedback } from './initial-validation.js';
const valid = { name: 'Anita', email: 'anita@example.com', rating: 5, comment: 'Excellent product' };
test('draft rejects whitespace-only names', () => assert.ok(validateFeedback({ ...valid, name: ' ' }).errors.length));
test('draft does not coerce rating strings', () => assert.ok(validateFeedback({ ...valid, rating: '5' }).errors.length));
test('draft rejects incomplete email addresses', () => assert.ok(validateFeedback({ ...valid, email: 'a@' }).errors.length));
