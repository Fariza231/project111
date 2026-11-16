export class CapacityError extends Error {
  constructor() { super('Feedback storage capacity reached'); this.name = 'CapacityError'; }
}

/** Deliberately bounded, process-local demo storage. Records disappear on restart. */
export function createFeedbackStore({ maxRecords = 5000 } = {}) {
  if (!Number.isSafeInteger(maxRecords) || maxRecords < 1) throw new RangeError('maxRecords must be a positive safe integer');
  const records = new Map();
  let nextId = 1;
  return {
    create(feedback) {
      if (records.size >= maxRecords) throw new CapacityError();
      const record = Object.freeze({ id: nextId++, name: feedback.name, email: feedback.email, rating: feedback.rating, comment: feedback.comment });
      records.set(record.id, record);
      return { ...record };
    },
    list() { return Array.from(records.values(), (record) => ({ ...record })); },
    find(id) { const record = records.get(id); return record ? { ...record } : undefined; },
  };
}
