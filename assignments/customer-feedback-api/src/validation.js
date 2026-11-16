const fields = ['name', 'email', 'rating', 'comment'];
const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/** Returns all field errors and a new, explicitly whitelisted record. */
export function validateFeedback(body) {
  const errors = [];
  if (body === null || typeof body !== 'object' || Array.isArray(body)) {
    return { errors: ['body must be a JSON object'] };
  }
  const unknown = Object.keys(body).filter((key) => !fields.includes(key));
  if (unknown.length) errors.push('unknown fields are not allowed');
  for (const [field, maximum] of [['name', 100], ['comment', 2000]]) {
    if (typeof body[field] !== 'string' || !body[field].trim()) errors.push(`${field} must be a nonempty string`);
    else if (body[field].length > maximum) errors.push(`${field} must not exceed ${maximum} characters`);
  }
  if (typeof body.email !== 'string' || body.email.length > 254 || !emailPattern.test(body.email.trim())) {
    errors.push('email must be a valid address of at most 254 characters');
  }
  if (typeof body.rating !== 'number' || !Number.isInteger(body.rating) || body.rating < 1 || body.rating > 5) {
    errors.push('rating must be an integer between 1 and 5');
  }
  if (errors.length) return { errors };
  return { errors, value: { name: body.name.trim(), email: body.email.trim(), rating: body.rating, comment: body.comment.trim() } };
}

export function parseFeedbackId(value) {
  if (typeof value !== 'string' || !/^[1-9]\d*$/.test(value)) return null;
  const id = Number(value);
  return Number.isSafeInteger(id) ? id : null;
}
