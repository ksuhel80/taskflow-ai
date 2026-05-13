# TaskFlow AI - MCP Server Architecture (`@taskflow-ai/mcp`)

This package implements a production-grade MCP server with:

- TypeScript MCP server (`@modelcontextprotocol/server`)
- Streamable HTTP and stdio transports
- JWT authentication
- RBAC authorization
- workspace isolation
- Zod validation
- rate limiting
- audit logging
- streaming support (transport-level)
- tool registry + service abstraction layer

## Folder layout

```txt
packages/mcp/src/
  bin/                     # runnable entrypoints
    http.ts
    stdio.ts

  server/
    config.ts              # env validation
    http.ts                # Streamable HTTP transport startup
    stdio.ts               # stdio transport startup

  auth/
    types.ts
    jwt.ts                 # JWT verification -> AuthContext

  rbac/
    permissions.ts         # role -> permissions map
    authorize.ts           # permission + workspace checks

  rate_limit/
    limiter.ts             # in-memory limiter (replace with Redis in prod)

  audit/
    logger.ts              # audit event contract + logger interface

  tools/
    schemas.ts             # Zod schemas for tool I/O
    registry.ts            # tool registration + middleware enforcement

  services/
    types.ts               # RequestContext
    taskflow.ts            # service interface + stub implementation

  errors/
    types.ts               # McpError taxonomy
```

## Transports (MCP transport setup)

- **stdio**: `src/server/stdio.ts`
  - best for local integrations that spawn the server process
- **Streamable HTTP**: `src/server/http.ts`
  - best for remote, scalable deployments
  - supports SSE-style streaming and sessions

## Authentication (JWT)

- Implemented in `src/auth/jwt.ts`
- Inputs:
  - `MCP_JWT_SECRET` (required)
  - optional issuer/audience checks
- Output:
  - `AuthContext` (`userId`, `tenantId`, `roles`, optional `allowedWorkspaces`)

## Authorization (RBAC + workspace isolation)

Enforced in `src/tools/registry.ts` for every tool call:

- `requireWorkspaceAccess(auth, workspaceId)`
- `requirePermission(auth, tool.permission)`

Workspace isolation:

- every tool input schema requires `workspaceId`
- optional allow-list in JWT claims (`workspaces[]`)

## Validation layer (Zod)

All tools define input and output schemas in `src/tools/schemas.ts`.
Tool registration uses:

- `inputSchema.safeParse(rawArgs)` -> tool-level validation error (`isError: true`)
- `outputSchema.parse(result)` -> server-side correctness guard

## Rate limiting

`src/rate_limit/limiter.ts` provides an in-memory limiter keyed by:

- tool name + tenantId + userId + workspaceId

Production recommendation:

- replace with a Redis-backed limiter so limits apply across replicas.

## Audit logging

`src/audit/logger.ts` defines `AuditEvent` and an `AuditLogger`.
`src/tools/registry.ts` logs:

- tool calls (ok/failure)
- duration
- error codes

Production recommendation:

- write audit logs to Postgres (append-only) or a queue (outbox pattern).

## Error handling

- Tool-level errors should return MCP `CallToolResult` with `isError: true`
- Protocol-level errors are represented as `McpError` and should be caught at boundaries

This package currently converts validation failures to `isError: true` results and throws `McpError` for auth/rate-limit failures.

## Streaming support

Streaming is supported by the MCP transport (Streamable HTTP).
Tool results are returned as:

- `content`: text JSON
- `structuredContent`: validated object

Future enhancement:

- add progress streaming via MCP SDK utilities (custom stream parts) for long-running tools.

## Tool registry system

`src/tools/registry.ts` registers tools:

- `get_tasks`
- `create_task`
- `update_task`
- `create_sprint`
- `search_memory`
- `get_team_load`
- `get_risk_alerts`

Each tool maps to a service method on `TaskFlowService` (see `src/services/taskflow.ts`).

## Service abstraction layer

`src/services/taskflow.ts` defines `TaskFlowService` and a stub implementation.
Replace the stub with real integrations:

- database package (Prisma)
- ai-runtime memory store
- risk engine
- team load computation
