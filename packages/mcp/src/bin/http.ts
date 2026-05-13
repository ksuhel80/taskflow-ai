import { loadMcpServerConfig } from '../server/config.js';
import { startHttpServer } from '../server/http.js';

const cfg = loadMcpServerConfig(process.env);
await startHttpServer({ ...cfg, transport: 'http' });
