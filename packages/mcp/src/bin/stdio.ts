import { loadMcpServerConfig } from '../server/config.js';
import { startStdioServer } from '../server/stdio.js';

const cfg = loadMcpServerConfig(process.env);
await startStdioServer({ ...cfg, transport: 'stdio' });
