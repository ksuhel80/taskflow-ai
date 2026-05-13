# Prisma Production Strategy - TaskFlow AI

This complements `prisma/schema.prisma` with relation/index/migration guidance.

## Relation Strategy

- **Single shared schema multi-tenancy**
  - every tenant-scoped row stores `tenant_id`
  - workspace-scoped rows store `workspace_id`
- **RBAC normalized**
  - `roles`, `permissions`, `role_permissions`
  - workspace assignment through `workspace_memberships` + `workspace_membership_roles`
- **Domain separation with join anchors**
  - product domain: `projects`, `tasks`, `sprints`, `comments`, `activities`
  - AI domain: `ai_workflows`, `ai_workflow_runs`, checkpoints/events, agent runs
  - memory domain: `memory_collections`, `memory_items`, `memory_embeddings`

## Soft Delete Strategy

Mutable tables include `deleted_at`:

- users, workspaces, memberships, roles, permissions
- projects, tasks, sprints, comments
- AI workflows/runs/agent runs/approvals
- memory collections/items/embeddings
- mcp_api_keys, subscriptions

Query convention:

- always filter `deleted_at IS NULL` in app repositories.

## Indexing Recommendations

### Always-on indexes

- tenant/time:
  - `(tenant_id, created_at)`
- tenant/workspace/status:
  - `(tenant_id, workspace_id, status, deleted_at)` on operational tables
- tenant/lookup:
  - natural keys with tenant composites (e.g. `workspace_id + key`, `tenant_id + email`)

### AI runtime indexes

- workflow run retrieval:
  - `(tenant_id, workspace_id, workflow_id, status, deleted_at)`
- checkpoint replay:
  - unique `(workflow_run_id, checkpoint_seq)`
- agent ops:
  - `(tenant_id, workspace_id, status, started_at, deleted_at)`

### Memory indexes

- metadata:
  - `(tenant_id, workspace_id, collection_id, deleted_at)`
  - `(tenant_id, source_type, source_id, deleted_at)`
  - `(tenant_id, preference_key, preference_scope, deleted_at)`
- vector:
  - create pgvector ANN indexes via SQL migrations (HNSW/IVFFlat) per embedding model key

## pgvector Support

In first SQL migration:

- `CREATE EXTENSION IF NOT EXISTS vector;`

In Prisma:

- `Unsupported("vector(1536)")`

For multiple embedding models/dimensions:

- keep `embedding_model_key`, `embedding_dimension`, `embedding_version`
- create dedicated ANN indexes per model/dimension path

## Scalability Considerations

1. **High-write tables**
   - `activities`, `audit_logs`, workflow events/checkpoints
   - consider monthly partitioning when growth rises
2. **Memory growth**
   - compression/retention jobs for old semantic memory
   - archive low-value embeddings
3. **Hot tenant isolation**
   - add targeted indexes for large tenants/workspaces
4. **API key security**
   - store only `key_hash` + `key_prefix`; never store raw keys

## Migration Strategy

1. **Baseline migration**
   - all enums, tables, constraints
   - pgvector extension SQL
2. **Backfill + rolling adoption**
   - add nullable columns first, backfill in background, then enforce required constraints
3. **Online index creation**
   - use SQL migrations with concurrent index creation for large tables
4. **Embedding evolution**
   - add new embedding version columns/tables
   - dual-read during rollout
   - cleanup legacy version after validation
5. **Release safety**
   - app version N reads both old/new fields
   - migration deploy
   - app version N+1 writes new only
