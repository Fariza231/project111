import { createApp } from './app.js';

const rawPort = process.env.PORT ?? '3000';
if (!/^\d+$/.test(rawPort) || Number(rawPort) < 1 || Number(rawPort) > 65535) {
  throw new Error('PORT must be an integer between 1 and 65535');
}
const logger = { info: (event) => console.log(JSON.stringify(event)), error: (event) => console.error(JSON.stringify(event)) };
const app = createApp({ logger });
const server = app.listen(Number(rawPort), '0.0.0.0', () => logger.info({ event: 'listening', port: Number(rawPort) }));
for (const signal of ['SIGTERM', 'SIGINT']) {
  process.once(signal, () => {
    logger.info({ event: 'shutdown', signal });
    const timer = setTimeout(() => process.exit(1), 10_000).unref();
    server.close(() => { clearTimeout(timer); process.exit(0); });
  });
}
