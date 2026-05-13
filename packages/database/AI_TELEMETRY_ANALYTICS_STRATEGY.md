# AI Telemetry & Analytics Strategy - TaskFlow AI

This document defines aggregation + retention strategy for AI telemetry models in `prisma/schema.prisma`.

## Scope

Telemetry models:

- `ai_telemetry_events`
- `ai_cost_usage`
- `ai_confidence_scores`
- `human_override_events`
- `approval_analytics_events`
- `hallucination_events`
- `ai_workflow_metric_rollups`

## Analytics Strategy

### Event-first, rollup-second

1. Write immutable raw events first (append-only).
2. Derive rollups asynchronously.
3. Use rollups for dashboards, raw events for forensics/debugging.

### Dimensions

Primary dimensions:

- `tenant_id`
- `workspace_id`
- `workflow_key`
- `model_provider`, `model_key`
- period (`hour/day/week/month`)

Key metrics:

- cost (`total_cost_usd`)
- token usage (`input/output/total`)
- latency (`avg`, `p95`)
- confidence (`avg_confidence`)
- human override rate
- approval conversion/latency
- hallucination rate

## Aggregation Strategy

### Near-real-time micro-batch (recommended)

- Every 1-5 minutes:
  - aggregate raw events from watermark `last_processed_at`
  - upsert into `ai_workflow_metric_rollups` by:
    - `(tenant_id, workspace_id, workflow_key, granularity, period_start)`

### Idempotency

- Aggregator stores checkpoint per source table and period window.
- Reprocessing same window should produce same rollup values.

### Late-arriving events

- Keep a sliding recompute window (e.g. last 48h) to account for delayed telemetry.

## Retention Strategy

Raw event tables:

- `ai_telemetry_events`: 90 days hot, 1 year cold archive
- `ai_cost_usage`: 180 days hot, 2 years cold archive
- `ai_confidence_scores`: 90 days hot, 1 year cold archive
- `human_override_events`: 1 year hot, 3 years cold archive
- `approval_analytics_events`: 1 year hot, 3 years cold archive
- `hallucination_events`: 1 year hot, 3 years cold archive

Rollup table:

- `ai_workflow_metric_rollups`: keep indefinitely (small footprint)

Deletion policy:

- Prefer archive + delete jobs by partition/time-window.
- Always preserve compliance-relevant subsets if required by policy.

## Scalability Considerations

1. Partitioning:
   - partition high-volume event tables by `created_at` (monthly).
2. Index hygiene:
   - keep write-path indexes minimal on raw tables.
   - use rollups for heavy analytical queries.
3. Backfill:
   - support historical backfill jobs from raw events into rollups.
4. Multi-tenant fairness:
   - apply tenant-scoped aggregation jobs or queue buckets for large tenants.

## Query Patterns

Preferred dashboard queries:

- read from `ai_workflow_metric_rollups` for trend charts
- drill down to raw events by `workflow_run_id`, `agent_run_id`, `request_id`, `trace_id`

## Migration Strategy

1. Add telemetry tables and indexes.
2. Deploy write-path instrumentation (events).
3. Deploy rollup job and backfill recent history.
4. Switch dashboards to rollups.
5. Enable retention/archive jobs.
