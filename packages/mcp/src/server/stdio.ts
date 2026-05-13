import { McpServer, StdioServerTransport } from '@modelcontextprotocol/server';

import { verifyJwt } from '../auth/jwt.js';
import { createConsoleAuditLogger } from '../audit/logger.js';
import { createInMemoryRateLimiter } from '../rate_limit/limiter.js';
import { createStubTaskFlowService } from '../services/taskflow.js';
import { registerTaskFlowTools } from '../tools/registry.js';
import type { ToolContext } from '../tools/registry.js';
import type { McpServerConfig } from './config.js';

export async function startStdioServer(cfg: McpServerConfig): Promise<void> {
  const server = new McpServer(
    { name: cfg.name, version: cfg.version },
    {
      instructions:
        'TaskFlow AI MCP server. Always pass workspaceId. Use read tools before write tools. Prefer structured outputs.',
    },
  );

  const token = process.env['MCP_JWT_TOKEN'];
  if (!token) throw new Error('MCP_JWT_TOKEN is required for stdio mode');

  const toolCtx: ToolContext = {
    auth: verifyJwt(token, {
      jwtSecret: cfg.jwtSecret,
      issuer: cfg.jwtIssuer,
      audience: cfg.jwtAudience,
    }),
    rateLimiter: createInMemoryRateLimiter({
      windowMs: cfg.rateLimitWindowMs,
      max: cfg.rateLimitMax,
    }),
    audit: createConsoleAuditLogger(),
    service: createStubTaskFlowService(),
  };

  registerTaskFlowTools(server, toolCtx);

  const transport = new StdioServerTransport();
  await server.connect(transport);
}
