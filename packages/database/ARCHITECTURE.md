# TaskFlow AI - Shared Database Architecture

This document designs the `@taskflow-ai/database` package: Prisma organization, multi-tenant model strategy, audit logs, AI agent tracking, workflow persistence, and memory storage backed by PostgreSQL + `pgvector`.

No business logic/query implementation is included.

## 1) Proposed Package Structure

```txt
packages/database/
  prisma/
    schema.prisma                 # all canonical models + generators
    README.md                     # how to run prisma + multi-tenant notes
    seed/
      seed.ts                     # seeding entrypoint (stub)
  src/
    index.ts                      # exports generated Prisma types (later)
    types/                        # shared TS types for domain identifiers (later)
```

## 2) Prisma Organization (Recommended)

Prisma uses a single `schema.prisma` file. To keep it maintainable:

- Group models by capability with comment sections:
  - `// Multi-tenancy`
  - `// Audit logs`
  - `// AI agent tracking`
  - `// Workflow persistence`
  - `// Memory storage (pgvector)`
- Use naming conventions that match Postgres:
  - DB columns: `snake_case` (via `@map` / `@@map`)
  - Prisma fields: `camelCase`
- Define extension requirements explicitly:
  - enable `pgvector` and store embeddings as `vector(<dim>)`

## 3) Multi-tenant Support Strategy

Default approach (shared Postgres schema):

1. Add `tenant_id` (UUID) to every tenant-scoped table.
2. For tenant-specific uniqueness, define composite uniques:
   - `@@unique([tenant_id, external_id])`
3. Include `tenant_id` in indexes for performance.

Isolation upgrade (optional later):
- Add PostgreSQL Row Level Security (RLS) policies per role, if you want stronger isolation.
- Keep the Prisma schema compatible with RLS-enabled tables by always writing `tenant_id`.

Tenant-scoped vs global tables:
- Global/system tables: `tenant_id` is nullable or absent (e.g., feature flags catalog).
- Tenant-scoped tables: `tenant_id` is required and enforced by DB constraints.

## 4) Domain Model Overview

### Audit logs (append-only)

Goal: immutable event history for compliance and debugging.

Recommended table: `audit_log`
- `tenant_id`
- `event_type` (enum)
- `actor_type` + `actor_id` (nullable if system)
- `subject_type` + `subject_id` (nullable)
- `context` (jsonb metadata, redacted-safe)
- `created_at`

### AI agent tracking

Track agent runs and steps without embedding raw sensitive content by default.

Recommended tables:
- `agent_run` (one run per agent execution attempt)
- `agent_step` (tool/model steps inside the run)
- `agent_tool_call` (normalized tool call records)

Include cross-links:
- `workflow_run_id` / `workflow_checkpoint_id` if agent steps are part of a workflow
- `llm_trace_id` if available (for correlation)

### Workflow persistence

Recommended tables:
- `workflow_run`
  - current status, versions, ids, input/output references
- `workflow_checkpoint`
  - checkpoint sequence + state JSONB and persistence metadata
- `workflow_event_log` (optional)
  - append-only events used for auditing/rehydration/stream ordering

Checkpoint design:
- Save at step boundaries to allow safe resume.
- Use `state_json` (jsonb) + a `checksum` for idempotency and integrity checks.

### Memory storage (pgvector)

Memory should support:
- storing embeddings (pgvector vector)
- linking embeddings to tenant/workflow/agent namespaces
- retrieving by query embedding (later)

Recommended tables:
- `memory_collection`
  - logical collection: tenant-scoped, namespace/type
- `memory_item`
  - one piece of memory (text, structured JSON refs, or pointer)
- `memory_embedding`
  - stores the `vector(<dim>)` column + metadata

Embedding dimension:
- Choose a single dimension across the system (e.g., `1536` or provider-specific).
- Enforce dimension consistency with a single canonical model policy.

## 5) Migration Strategy (Prisma + PostgreSQL)

Prisma migrations approach:

1. Establish an initial baseline migration:
   - create required enums
   - create `pgvector` extension (one-time)
   - create all core tables and indexes
2. Add feature migrations as separate deployable units:
   - audit logging tables
   - agent tracking tables
   - workflow persistence tables
   - memory/pgvector tables
3. Use `prisma migrate dev` locally and `prisma migrate deploy` in CI/CD.

Multi-tenant considerations:
- Since we use `tenant_id` column-based partitioning, migrations can be shared across tenants.
- If you later move to schema-per-tenant, migrations may need to be parameterized or run per schema.

Embedding schema migrations:
- If embedding dimension changes, you may need:
  - a new embedding column or a new embedding table
  - backfill procedure (handled later by a dedicated migration job)

## 6) Seeding Strategy

Seed should set up system catalogs and defaults, not per-tenant data unless onboarding requires it.

Recommended seeding rules:
- Seed global catalogs (safe to run multiple times with idempotent upserts):
  - default workflow versions metadata
  - agent templates
  - model/provider policies (LiteLLM routing configs)
  - audit event types (if stored as rows)
- For per-tenant initialization:
  - create tenant-specific defaults during onboarding (outside Prisma seed), or
  - support a `TENANT_ID` env override for `seed.ts` to seed one tenant at a time.

Idempotency:
- Use unique constraints and upserts to keep seeding safe in CI and developer environments.

## 7) Naming Conventions

### Database naming
- Tables: `snake_case` (e.g., `workflow_run`, `workflow_checkpoint`)
- Columns: `snake_case` (e.g., `tenant_id`, `created_at`)

### Prisma naming
- Prisma model fields: `camelCase` (e.g., `tenantId`, `createdAt`)
- Use `@map` / `@@map` for explicit mapping to DB naming.

### Identifiers
- Primary keys: UUID (`uuid_generate_v4()` or `gen_random_uuid()` depending on extension)
- External identifiers: `external_id` with unique constraint scoped by `tenant_id`

## 8) Transaction Strategy

Principle: any stateful workflow/agent transition must be persisted atomically with:
- checkpoint updates
- workflow status updates
- audit log entries (and optionally event log)

Recommended patterns:

1. Single transaction per step boundary:
   - insert/update `workflow_checkpoint`
   - update `workflow_run` status/next pointers
   - insert `audit_log` entries
   - optionally insert `workflow_event_log`

2. Optimistic concurrency:
   - include `state_version` / `checkpoint_seq` on `workflow_checkpoint`
   - require it matches expected version during resume
   - if mismatch => treat as conflict and fail/reload (handled in app layer later)

3. Outbox pattern for streaming (if/when needed):
   - write stream events to `outbox_event` table in the same DB transaction
   - separate relay worker publishes to Redis/SSE
   - prevents losing events if the process crashes between DB commit and queue publish

## 9) Operational Considerations (Non-functional)

- Index audit logs and workflow events by `(tenant_id, created_at)` and `(job_id/run_id)`.
- Partitioning (optional later): audit/workflow logs can become large; consider time-based partitioning.
- Keep JSONB payloads redaction-safe (no secrets, minimal PII).

---

End of database architecture design.

