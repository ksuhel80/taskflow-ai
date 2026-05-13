# `@taskflow-ai/mcp`

Production-grade MCP server for TaskFlow AI.

## Transports

- **stdio**: local integrations (spawned process)
- **Streamable HTTP**: remote server with streaming

## Security

- JWT authentication
- RBAC authorization
- Workspace isolation
- Rate limiting
- Audit logging

# `@taskflow-ai/mcp`

Production-grade MCP server for TaskFlow AI.

## Features (architecture scaffold)

- MCP Server (TypeScript) with stdio + Streamable HTTP (SSE) transports
- JWT authentication
- RBAC permissions per tool
- Workspace isolation (required in auth context)
- Zod validation for tool inputs/outputs
- Rate limiting (pluggable; in-memory default)
- Audit logging (structured)
- Streaming support (HTTP SSE transport)
- Tool registry system

## Tools

- `get_tasks`
- `create_task`
- `update_task`
- `create_sprint`
- `search_memory`
- `get_team_load`
- `get_risk_alerts`

## Dev/Build

```bash
npm -w @taskflow-ai/mcp run build
```
