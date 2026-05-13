import { z } from 'zod';

export const mcpServerConfigSchema = z.object({
  name: z.string().default('taskflow-ai-mcp'),
  version: z.string().default('0.1.0'),

  // Transport
  transport: z.enum(['stdio', 'http']).default('http'),
  httpPort: z.number().int().min(1).max(65535).default(8787),
  httpEnableJsonResponse: z.boolean().default(false),

  // Security
  jwtSecret: z.string().min(16),
  jwtIssuer: z.string().optional(),
  jwtAudience: z.string().optional(),

  // Rate limiting
  rateLimitWindowMs: z.number().int().min(100).default(10_000),
  rateLimitMax: z.number().int().min(1).default(100),
});

export type McpServerConfig = z.infer<typeof mcpServerConfigSchema>;

export function loadMcpServerConfig(env: NodeJS.ProcessEnv): McpServerConfig {
  const parsed = mcpServerConfigSchema.safeParse({
    name: env['MCP_SERVER_NAME'],
    version: env['MCP_SERVER_VERSION'],
    transport: env['MCP_TRANSPORT'],
    httpPort: env['MCP_HTTP_PORT'] ? Number(env['MCP_HTTP_PORT']) : undefined,
    httpEnableJsonResponse: env['MCP_HTTP_ENABLE_JSON'] === 'true',
    jwtSecret: env['MCP_JWT_SECRET'],
    jwtIssuer: env['MCP_JWT_ISSUER'],
    jwtAudience: env['MCP_JWT_AUDIENCE'],
    rateLimitWindowMs: env['MCP_RATE_LIMIT_WINDOW_MS']
      ? Number(env['MCP_RATE_LIMIT_WINDOW_MS'])
      : undefined,
    rateLimitMax: env['MCP_RATE_LIMIT_MAX'] ? Number(env['MCP_RATE_LIMIT_MAX']) : undefined,
  });
  if (!parsed.success) {
    throw new Error(`Invalid MCP server config: ${parsed.error.message}`);
  }
  return parsed.data;
}
