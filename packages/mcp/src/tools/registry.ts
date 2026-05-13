import type { McpServer } from '@modelcontextprotocol/server';
import { z } from 'zod';

import type { AuthContext } from '../auth/types.js';
import { requirePermission, requireWorkspaceAccess } from '../rbac/authorize.js';
import type { Permission } from '../rbac/permissions.js';
import type { RateLimiter } from '../rate_limit/limiter.js';
import type { AuditLogger } from '../audit/logger.js';
import { McpError } from '../errors/types.js';
import type { TaskFlowService } from '../services/taskflow.js';
import type { RequestContext } from '../services/types.js';
import {
  createSprintInput,
  createSprintOutput,
  createTaskInput,
  createTaskOutput,
  getRiskAlertsInput,
  getRiskAlertsOutput,
  getTasksInput,
  getTasksOutput,
  getTeamLoadInput,
  getTeamLoadOutput,
  searchMemoryInput,
  searchMemoryOutput,
  updateTaskInput,
  updateTaskOutput,
} from './schemas.js';

export type ToolContext = {
  auth: AuthContext;
  rateLimiter: RateLimiter;
  audit: AuditLogger;
  service: TaskFlowService;
};

type ToolDef<I extends z.ZodTypeAny, O extends z.ZodTypeAny> = {
  name: string;
  title: string;
  description: string;
  permission: Permission;
  inputSchema: I;
  outputSchema: O;
  rateLimitKey: (auth: AuthContext, input: z.infer<I>) => string;
  handler: (ctx: ToolContext, input: z.infer<I>) => Promise<z.infer<O>>;
};

function toRequestContext(auth: AuthContext, workspaceId: string): RequestContext {
  return {
    tenantId: auth.tenantId,
    userId: auth.userId,
    workspaceId,
    roles: auth.roles,
  };
}

async function audited<I extends z.ZodTypeAny, O extends z.ZodTypeAny>(
  tool: ToolDef<I, O>,
  ctx: ToolContext,
  input: z.infer<I>,
): Promise<z.infer<O>> {
  const start = Date.now();
  const workspaceId = (input as { workspaceId?: string }).workspaceId ?? '';
  requireWorkspaceAccess(ctx.auth, workspaceId);
  requirePermission(ctx.auth, tool.permission);

  ctx.rateLimiter.take(tool.rateLimitKey(ctx.auth, input));

  try {
    const result = await tool.handler(ctx, input);
    await ctx.audit.log({
      ts: new Date().toISOString(),
      actor: { userId: ctx.auth.userId, tenantId: ctx.auth.tenantId },
      workspaceId,
      tool: tool.name,
      action: 'call',
      ok: true,
      durationMs: Date.now() - start,
    });
    return result;
  } catch (err) {
    const e =
      err instanceof McpError ? err : new McpError('INTERNAL_ERROR', 'Tool execution failed');
    await ctx.audit.log({
      ts: new Date().toISOString(),
      actor: { userId: ctx.auth.userId, tenantId: ctx.auth.tenantId },
      workspaceId,
      tool: tool.name,
      action: 'call',
      ok: false,
      errorCode: e.code,
      durationMs: Date.now() - start,
      meta: { message: e.message },
    });
    throw e;
  }
}

export function registerTaskFlowTools(server: McpServer, toolCtx: ToolContext): void {
  const tools: ToolDef<any, any>[] = [
    {
      name: 'get_tasks',
      title: 'Get tasks',
      description: 'List tasks in a workspace.',
      permission: 'tasks:read',
      inputSchema: getTasksInput,
      outputSchema: getTasksOutput,
      rateLimitKey: (auth, input) =>
        `tool:get_tasks:${auth.tenantId}:${auth.userId}:${input.workspaceId}`,
      handler: async (ctx, input) =>
        ctx.service.getTasks(toRequestContext(ctx.auth, input.workspaceId), input),
    },
    {
      name: 'create_task',
      title: 'Create task',
      description: 'Create a task in a workspace.',
      permission: 'tasks:write',
      inputSchema: createTaskInput,
      outputSchema: createTaskOutput,
      rateLimitKey: (auth, input) =>
        `tool:create_task:${auth.tenantId}:${auth.userId}:${input.workspaceId}`,
      handler: async (ctx, input) =>
        ctx.service.createTask(toRequestContext(ctx.auth, input.workspaceId), input),
    },
    {
      name: 'update_task',
      title: 'Update task',
      description: 'Update an existing task.',
      permission: 'tasks:write',
      inputSchema: updateTaskInput,
      outputSchema: updateTaskOutput,
      rateLimitKey: (auth, input) =>
        `tool:update_task:${auth.tenantId}:${auth.userId}:${input.workspaceId}`,
      handler: async (ctx, input) =>
        ctx.service.updateTask(toRequestContext(ctx.auth, input.workspaceId), input),
    },
    {
      name: 'create_sprint',
      title: 'Create sprint',
      description: 'Create a sprint in a workspace.',
      permission: 'sprints:write',
      inputSchema: createSprintInput,
      outputSchema: createSprintOutput,
      rateLimitKey: (auth, input) =>
        `tool:create_sprint:${auth.tenantId}:${auth.userId}:${input.workspaceId}`,
      handler: async (ctx, input) =>
        ctx.service.createSprint(toRequestContext(ctx.auth, input.workspaceId), input),
    },
    {
      name: 'search_memory',
      title: 'Search memory',
      description: 'Search workspace memory (RAG) and return top hits.',
      permission: 'memory:search',
      inputSchema: searchMemoryInput,
      outputSchema: searchMemoryOutput,
      rateLimitKey: (auth, input) =>
        `tool:search_memory:${auth.tenantId}:${auth.userId}:${input.workspaceId}`,
      handler: async (ctx, input) =>
        ctx.service.searchMemory(toRequestContext(ctx.auth, input.workspaceId), input),
    },
    {
      name: 'get_team_load',
      title: 'Get team load',
      description: 'Return team capacity/load for a workspace.',
      permission: 'team:load:read',
      inputSchema: getTeamLoadInput,
      outputSchema: getTeamLoadOutput,
      rateLimitKey: (auth, input) =>
        `tool:get_team_load:${auth.tenantId}:${auth.userId}:${input.workspaceId}`,
      handler: async (ctx, input) =>
        ctx.service.getTeamLoad(toRequestContext(ctx.auth, input.workspaceId), input),
    },
    {
      name: 'get_risk_alerts',
      title: 'Get risk alerts',
      description: 'Return risk alerts for a workspace.',
      permission: 'risk:alerts:read',
      inputSchema: getRiskAlertsInput,
      outputSchema: getRiskAlertsOutput,
      rateLimitKey: (auth, input) =>
        `tool:get_risk_alerts:${auth.tenantId}:${auth.userId}:${input.workspaceId}`,
      handler: async (ctx, input) =>
        ctx.service.getRiskAlerts(toRequestContext(ctx.auth, input.workspaceId), input),
    },
  ];

  for (const tool of tools) {
    server.registerTool(
      tool.name,
      {
        title: tool.title,
        description: tool.description,
        inputSchema: tool.inputSchema,
        outputSchema: tool.outputSchema,
        annotations: {
          // Most tools are safe and idempotent except creates/updates.
          destructiveHint:
            tool.name === 'update_task' ||
            tool.name === 'create_task' ||
            tool.name === 'create_sprint',
          idempotentHint:
            tool.name === 'get_tasks' ||
            tool.name === 'search_memory' ||
            tool.name === 'get_team_load' ||
            tool.name === 'get_risk_alerts',
        },
      },
      async (rawArgs: unknown, _serverCtx: unknown) => {
        const parsed = tool.inputSchema.safeParse(rawArgs);
        if (!parsed.success) {
          return {
            content: [
              { type: 'text' as const, text: `Validation failed: ${parsed.error.message}` },
            ],
            isError: true,
          };
        }

        const result = await audited(tool, toolCtx, parsed.data);
        const structured = tool.outputSchema.parse(result);
        return {
          content: [{ type: 'text' as const, text: JSON.stringify(structured) }],
          structuredContent: structured,
        };
      },
    );
  }
}
