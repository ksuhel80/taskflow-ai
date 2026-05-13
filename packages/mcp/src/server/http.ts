import { randomUUID } from 'node:crypto';

import { createMcpExpressApp } from '@modelcontextprotocol/express';
import { NodeStreamableHTTPServerTransport } from '@modelcontextprotocol/node';
import { McpServer } from '@modelcontextprotocol/server';
import type { Request, Response } from 'express';

import { verifyJwt } from '../auth/jwt.js';
import { createConsoleAuditLogger } from '../audit/logger.js';
import { createInMemoryRateLimiter } from '../rate_limit/limiter.js';
import { createStubTaskFlowService } from '../services/taskflow.js';
import { registerTaskFlowTools } from '../tools/registry.js';
import type { ToolContext } from '../tools/registry.js';
import type { McpServerConfig } from './config.js';

export async function startHttpServer(cfg: McpServerConfig): Promise<void> {
  const server = new McpServer(
    { name: cfg.name, version: cfg.version },
    {
      instructions:
        'TaskFlow AI MCP server. Always pass workspaceId. Use read tools before write tools. Prefer structured outputs.',
    },
  );

  const audit = createConsoleAuditLogger();
  const rateLimiter = createInMemoryRateLimiter({
    windowMs: cfg.rateLimitWindowMs,
    max: cfg.rateLimitMax,
  });
  const service = createStubTaskFlowService();

  // Note: MCP server handlers are not directly aware of HTTP request context.
  // This scaffold uses a single JWT configured via env in HTTP mode as well, to keep semantics simple.
  // Production approach:
  // - create one McpServer per authenticated session (sessionIdGenerator)
  // - OR customize transport/session binding to inject auth into tool context.
  const token = process.env['MCP_JWT_TOKEN'];
  if (!token) throw new Error('MCP_JWT_TOKEN is required for HTTP mode in this scaffold');

  const toolCtx: ToolContext = {
    auth: verifyJwt(token, {
      jwtSecret: cfg.jwtSecret,
      issuer: cfg.jwtIssuer,
      audience: cfg.jwtAudience,
    }),
    rateLimiter,
    audit,
    service,
  };
  registerTaskFlowTools(server, toolCtx);

  // Root express app for hosting MCP routes.
  const app = createMcpExpressApp();

  // Stateful example: reuse a transport instance across requests.
  // For stateless mode, set sessionIdGenerator: undefined and create a new transport per request.
  const transport = new NodeStreamableHTTPServerTransport({
    sessionIdGenerator: () => randomUUID(),
    enableJsonResponse: cfg.httpEnableJsonResponse,
  });
  await server.connect(transport);

  app.post('/mcp', async (req: Request, res: Response) => {
    // The express adapter sets up JSON parsing; `req.body` should be available.
    await transport.handleRequest(req, res, req.body);
  });

  await new Promise<void>((resolve) => {
    app.listen(cfg.httpPort, () => resolve());
  });
}
