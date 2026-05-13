# TaskFlow AI - Observability Architecture

This document defines observability architecture for TaskFlow AI with:

- Sentry integration
- LangSmith tracing
- PostHog analytics
- OpenTelemetry
- AI workflow tracing
- queue monitoring
- token cost tracking
- latency tracking
- failure tracking

---

## 1) Logging Architecture

Use structured JSON logging as the baseline. All logs should include:

- `ts`, `severity`, `event`, `message`
- `tenant_id`, `workspace_id`
- `request_id`, `trace_id`, `correlation_id`
- optional `workflow_run_id`, `agent_run_id`, `queue_job_id`

Log sinks:

- app logs -> stdout (container collection)
- error/fatal logs -> Sentry events
- security-sensitive actions -> audit logs (DB/outbox)

Code scaffold:

- `apps/ai-runtime/app/observability/logging.py`
- `apps/ai-runtime/app/observability/types.py`
- `apps/ai-runtime/app/observability/providers/sentry_provider.py`

---

## 2) Tracing Middleware

## 2.1 Request tracing

FastAPI middleware creates/propagates:

- `x-request-id`
- `x-trace-id`

It starts and closes spans around HTTP requests and propagates context to workers/workflows.

Code scaffold:

- `apps/ai-runtime/app/observability/middleware/tracing_middleware.py`
- `apps/ai-runtime/app/observability/tracing.py`
- `apps/ai-runtime/app/observability/providers/opentelemetry_provider.py`
- `apps/ai-runtime/app/observability/providers/langsmith_provider.py`

## 2.2 AI workflow tracing

Instrument span boundaries at:

- workflow start/resume/cancel
- each workflow step
- each agent run/step/tool call
- each LLM call and memory retrieval

LangSmith traces should include:

- model/provider metadata
- token/cost fields
- confidence and error annotations

---

## 3) AI Telemetry System

Emit AI telemetry events for:

- token usage (input/output/total)
- cost in USD
- latency
- confidence
- success/failure + error code

Code scaffold:

- `apps/ai-runtime/app/observability/ai_telemetry.py`
- `apps/ai-runtime/app/observability/types.py`

Recommended persistence:

- write telemetry events to append-only tables (`ai_cost_usage`, `ai_confidence_scores`, etc.)
- aggregate into rollups for dashboards

---

## 4) Queue Monitoring

Queue lifecycle hooks:

- job started
- job completed
- job failed
- retries and lag

Metrics:

- queue lag
- processing duration p95/p99
- retries/DLQ inflow
- failure rate by queue/job type

Code scaffold:

- `apps/ai-runtime/app/observability/queue_monitoring.py`

---

## 5) Dashboard Metrics

Metric catalog scaffold:

- `apps/ai-runtime/app/observability/dashboards/metrics_catalog.py`

Core dashboard groups:

- AI Cost & Tokens
  - `ai.cost.total_usd`
  - `ai.tokens.input_total`
  - `ai.tokens.output_total`
- AI Quality & Reliability
  - `ai.confidence.avg`
  - `ai.failures.rate`
  - hallucination and override metrics (from analytics DB)
- Queue Health
  - `queue.lag.ms`
  - `queue.jobs.failed`
  - `queue.jobs.retry_count`

---

## 6) Monitoring Strategy

## 6.1 Alerting

Alert on:

- AI cost spikes
- p95 latency regressions
- failure rate threshold breaches
- queue lag and DLQ spikes
- approval latency anomalies

## 6.2 Sampling

Use adaptive sampling:

- 100% error traces
- lower sampling for high-volume successful runs
- elevate sampling for flagged tenants/workflows

## 6.3 Retention

Store:

- high-cardinality traces short-term (7-30 days)
- aggregated metrics long-term
- audit/security events per compliance policy

## 6.4 Correlation

Everything must be joinable via:

- `trace_id`
- `request_id`
- `workflow_run_id`
- `agent_run_id`
- `queue_job_id`

This enables end-to-end incident analysis from UI action -> queue -> workflow -> model call.
