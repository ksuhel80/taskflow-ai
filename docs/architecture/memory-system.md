# TaskFlow AI - Memory System (pgvector + Retrieval)

This document designs how TaskFlow AI stores and retrieves memory for workflows and agents.

Memory is used by `apps/ai-runtime` during prompt construction and agent context building.

## Memory Goals

- Persist useful knowledge for future tasks (long-term memory)
- Provide working context for agent reasoning (short-term/working context)
- Support tenant isolation
- Enable traceable retrieval for audit/debugging

## Storage Architecture (PostgreSQL + pgvector)

Memory is persisted in Postgres using `pgvector`:
- Embeddings stored as `vector(<dim>)`
- Metadata stored in JSON and relational columns for indexing and filtering

### Canonical entities (from `packages/database`)
- `memory_collection`
  - logical bucket for embeddings (namespace + type)
  - tenant-scoped
- `memory_item`
  - a memory record (text content or pointer)
  - tenant-scoped, linked to a collection
- `memory_embedding`
  - one or more embeddings per memory item
  - stores `embedding Unsupported("vector(1536)")` in Prisma design

## Namespaces & Multi-tenancy

Every memory record is tenant-scoped:
- All tables include `tenant_id`
- Retrieval must always filter by `tenant_id`

Collections define scope:
- `namespace_type` is a controlled enum (e.g., `AGENT`, `WORKFLOW`, `USER`, `SYSTEM`)
- `namespace_key` forms the canonical key:
  - agentKey/workflowKey/userId (canonical concatenation)

## Retrieval Flow (Conceptual)

```mermaid
flowchart TD
  Q[Memory Query] --> E[Embedding step (LiteLLM provider via router)]
  E --> S[Similarity search in pgvector]
  S --> F[Filter by tenant_id + namespace]
  F --> C[Context construction (ranking + formatting)]
  C --> A[Injected into prompt / agent tools]
```

### Query inputs (contract-first)
- `tenant_id`
- `namespace_type` + `namespace_key`
- `query_text` (or precomputed query embedding later)
- retrieval parameters:
  - `top_k`
  - optional `min_score` / distance threshold

## Embedding & Dimension Strategy

- Use one canonical embedding dimension across the system (Prisma schema uses `vector(1536)` placeholder).
- If you change the embedding model:
  - keep old embeddings
  - write new embeddings with a provenance field:
    - `embedding_model_key`
  - retrieval can choose which model(s) to query.

## Scalability Notes

1. pgvector performance
   - Add ANN indexes (e.g., HNSW) in migrations once retrieval patterns are known.
   - Keep metadata filters narrow (always include `tenant_id` + namespace).

2. Write amplification
   - memory writes happen at ingestion time (later).
   - Batch embedding creation where possible to reduce LLM/routing overhead.

3. Retrieval hot paths
   - cache common retrieval results per job (short TTL in Redis) later.
   - reuse embedding computations for identical queries within a job.

## Engineering Guidelines

- **No raw secrets** in memory content or logs.
- **Redaction by design**:
  - store minimal necessary text
  - store provenance metadata, not sensitive payloads
- **Consistency**:
  - retrieval must use the same embedding dimension/model policy as ingestion
- **Auditability**:
  - retrieval should emit standardized events so workflow streaming/auditing can explain context selection later

