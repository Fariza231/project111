import express from 'express';
import helmet from 'helmet';
import { rateLimit } from 'express-rate-limit';
import { randomUUID, timingSafeEqual } from 'node:crypto';
import { createFeedbackStore, CapacityError } from './feedback.js';
import { validateFeedback, parseFeedbackId } from './validation.js';

export function createApp({
  store = createFeedbackStore(),
  readApiKey = process.env.READ_API_KEY,
  production = process.env.NODE_ENV === 'production',
  rateLimitMax = 60,
  logger,
} = {}) {
  if (production && (typeof readApiKey !== 'string' || readApiKey.length < 24)) {
    throw new Error('Production requires READ_API_KEY of at least 24 characters');
  }
  const app = express();
  app.disable('x-powered-by');
  app.set('trust proxy', false);
  app.use(helmet());
  app.use((req, res, next) => {
    req.requestId = randomUUID();
    res.set('X-Request-Id', req.requestId);
    res.on('finish', () => logger?.info?.({ requestId: req.requestId, method: req.method, route: req.route?.path ?? 'unmatched', status: res.statusCode }));
    next();
  });
  app.get('/health', (_req, res) => res.json({ status: 'ok', storage: 'memory' }));
  app.use('/feedback', rateLimit({
    windowMs: 60_000, limit: rateLimitMax, standardHeaders: 'draft-8', legacyHeaders: false,
    // This app intentionally ignores untrusted forwarding headers. Proxy topology needs deployment review.
    validate: { xForwardedForHeader: false },
    handler: (_req, res) => res.status(429).json({ error: { code: 'RATE_LIMITED', message: 'Too many requests; try again later.' } }),
  }));
  app.use(express.json({ limit: '16kb', strict: true }));
  const requireReadKey = (req, res, next) => {
    if (!readApiKey) return next();
    const supplied = req.get('X-API-Key');
    const expectedBuffer = Buffer.from(readApiKey);
    const suppliedBuffer = typeof supplied === 'string' ? Buffer.from(supplied) : Buffer.alloc(0);
    if (suppliedBuffer.length !== expectedBuffer.length || !timingSafeEqual(suppliedBuffer, expectedBuffer)) {
      return res.status(401).json({ error: { code: 'UNAUTHORIZED', message: 'A valid X-API-Key is required.' } });
    }
    return next();
  };
  app.post('/feedback', (req, res) => {
    const result = validateFeedback(req.body);
    if (result.errors.length) return res.status(400).json({ error: { code: 'VALIDATION_ERROR', details: result.errors } });
    const record = store.create(result.value);
    return res.status(201).location(`/feedback/${record.id}`).json(record);
  });
  app.get('/feedback', requireReadKey, (_req, res) => res.json(store.list()));
  app.get('/feedback/:id', requireReadKey, (req, res) => {
    const id = parseFeedbackId(req.params.id);
    if (id === null) return res.status(400).json({ error: { code: 'INVALID_ID', message: 'ID must be a positive safe integer.' } });
    const record = store.find(id);
    if (!record) return res.status(404).json({ error: { code: 'NOT_FOUND', message: 'Feedback not found.' } });
    return res.json(record);
  });
  app.use((_req, res) => res.status(404).json({ error: { code: 'NOT_FOUND', message: 'Route not found.' } }));
  app.use((error, req, res, _next) => {
    if (error.type === 'entity.too.large') return res.status(413).json({ error: { code: 'BODY_TOO_LARGE', message: 'JSON body exceeds 16kb.' } });
    if (error.type === 'entity.parse.failed' || error instanceof URIError) {
      return res.status(400).json({ error: { code: 'INVALID_JSON_OR_URI', message: 'Malformed JSON or request URI.' } });
    }
    if (error instanceof CapacityError) return res.status(503).json({ error: { code: 'CAPACITY_REACHED', message: 'Feedback storage is full.' } });
    logger?.error?.({ requestId: req.requestId, event: 'request_failed' });
    return res.status(500).json({ error: { code: 'INTERNAL_ERROR', message: 'An unexpected error occurred.' } });
  });
  return app;
}
