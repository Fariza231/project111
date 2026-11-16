/** Initial AI-assisted draft: tests will review this implementation before refinement. */
export function validateFeedback(body) {
  const errors = [];
  if (!body || typeof body !== 'object') return { errors: ['body must be an object'] };
  if (!body.name) errors.push('name is required');
  if (typeof body.email !== 'string' || !body.email.includes('@')) errors.push('email is invalid');
  if (!(body.rating >= 1 && body.rating <= 5)) errors.push('rating must be between 1 and 5');
  if (!body.comment) errors.push('comment is required');
  return { errors, value: errors.length ? undefined : { name: body.name, email: body.email, rating: body.rating, comment: body.comment } };
}
