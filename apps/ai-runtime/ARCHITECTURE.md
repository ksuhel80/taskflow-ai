# TaskFlow AI - ai-runtime Architecture (Design Only)

This document designs the `apps/ai-runtime` service architecture for an AI-native SaaS. It intentionally contains **no business logic implementation**.

## Goals

- FastAPI service for AI runtime APIs and streaming endpoints
- LangGraph workflows with workflow persistence/checkpointing
- CrewAI agent orchestration
- LiteLLM routing across model providers
- Redis queue consumers for background execution
- Streaming responses to callers
- Memory retrieval (RAG / working memory) integrated into workflows/agents
- Structured logging + observability hooks
- Robust error handling with retries, dead-lettering, and consistent error contracts

## Folder Structure (Proposed)

> Keep `app/` as the Python package root. Keep all integrations behind interfaces so the business logic (graphs/agents) can remain testable and swappable.

```
apps/ai-runtime/
  app/
    __init__.py
    main.py                         # FastAPI app wiring (routes, DI, startup/shutdown)

    api/
      __init__.py
      routes/
        __init__.py
        health.py                  # liveness/readiness
        jobs.py                    # start/resume jobs, return job_id
        stream.py                 # SSE/WebSocket stream for job events
      deps/
        __init__.py
        container.py               # dependency wiring (config, clients, sinks)

    core/
      __init__.py
      config.py                    # pydantic-settings validation
      ids.py                       # correlation/job/request ids helpers
      time.py                      # time utilities

    interfaces/
      __init__.py
      contracts.py                # shared request/response and event schemas
      llm.py                        # LiteLLM router interfaces
      memory.py                     # memory retrieval interfaces
      queue.py                      # queue publish/consume interfaces
      streaming.py                  # streaming publisher and event contract
      persistence.py                # workflow checkpoint persistence interfaces
      workflow.py                   # workflow engine interfaces
      agents.py                      # agent orchestration interfaces
      observability.py              # structured logging + tracing/metrics hook contracts

    errors/
      __init__.py
      types.py                     # domain error taxonomy
      classifier.py                # maps exceptions -> retryable/non-retryable + error codes
      middleware.py                # FastAPI exception handling -> API/stream error events

    observability/
      __init__.py
      logging.py                   # JSON structured logging config + redaction policy
      metrics.py                   # metrics hook scaffolding
      tracing.py                   # OpenTelemetry hook scaffolding (optional)
      sink.py                      # ObservabilitySink implementation that calls hooks

    integrations/
      __init__.py
      redis/
        __init__.py
        client.py                  # Redis client wrapper
        streams.py                 # Redis Streams helpers (ack, group, offsets)
      litellm/
        __init__.py
        router.py                  # LiteLLM invocation behind interface
      crewai/
        __init__.py
        adapter.py                 # CrewAI adapter behind interface
      langgraph/
        __init__.py
        builder.py                 # LangGraph builder behind workflow engine
      persistence/
        __init__.py
        redis_checkpoint.py       # checkpoint store via Redis (or placeholder)

    queue/
      __init__.py
      messages/
        __init__.py
        types.py                   # Redis message types mapped to contracts
      publishers/
        __init__.py
        job_publisher.py           # publish job start/resume and event commands
      consumers/
        __init__.py
        base.py                    # common consumer loop (decode, classify, retry)
        workflow_consumer.py      # consumes workflow execution/resume messages
        agent_consumer.py         # consumes agent-related messages (optional split)
        retry_policy.py           # retry/backoff policy (no business logic)
      idempotency/
        __init__.py
        store.py                  # idempotency key checks (interface-only if needed)

    memory/
      __init__.py
      retrievers/
        __init__.py
        base.py                   # MemoryRetriever interface + adapter scaffolding
        vector_store.py          # Vector store adapter (placeholder)
        chat_memory.py          # Working memory adapter (placeholder)

    streaming/
      __init__.py
      sse.py                        # Server-Sent Events publisher (event->stream)
      events.py                     # event types and serialization helpers

    workflows/
      __init__.py
      engine/
        __init__.py
        runner.py                  # workflow run orchestration (start/resume)
        state.py                   # canonical workflow state container
        checkpoints.py            # uses persistence interfaces
      graphs/
        __init__.py
        graph_factory.py          # LangGraph graph factory (business logic later)
        nodes/                    # graph nodes (no implementations yet)
          __init__.py
          placeholder.py

    agents/
      __init__.py
      orchestration/
        __init__.py
        orchestrator.py            # agent orchestration glue (no business logic yet)
        tools/                     # tool adapters (placeholder)
          __init__.py
          placeholder.py
      crews/
        __init__.py
        crew_factory.py           # CrewAI crew factory (no business logic yet)
  requirements/                       # (optional) pinned deployment docs
  tests/                               # (later) unit/integration tests
  scripts/                             # (later) local/dev scripts

```

## Service Boundaries (Dependency Rules)

Define strict boundaries so components do not “reach across” layers.

1. `api/`
   - Depends on: `core/`, `interfaces/`, `observability/`
   - Does **not** depend on LangGraph/CrewAI concrete implementations directly.

2. `queue/`
   - Depends on: `interfaces/`, `core/`, `errors/`, `observability/`
   - Consumes/produces typed queue messages only.

3. `workflows/`
   - Depends on: `interfaces/`, `errors/`, `observability/`, `integrations/langgraph/`
   - Business workflow graphs are built here, but the runtime engine remains interface-first.

4. `agents/`
   - Depends on: `interfaces/`, `errors/`, `observability/`, `integrations/crewai/`, `memory/`, `integrations/litellm/`

5. `integrations/`
   - Owns concrete clients/adapters (Redis streams, LiteLLM router calls, CrewAI adapter, LangGraph builder).
   - Should be the only place where “vendor SDKs” are imported.

6. `memory/`
   - Depends on: `interfaces/`, `integrations/*` needed by storage (vector DB, redis cache).
   - Provides retrieval as a service to workflows/agents.

7. `observability/`
   - Depends on: `interfaces/` only.
   - Provides hook-based sink so it can be swapped/disabled in local/test environments.

8. `errors/`
   - Defines taxonomy + classification; used by `api/` and `queue/` to ensure consistent responses.

Rule of thumb:
- “No direct vendor SDK imports outside `integrations/`.”
- “All cross-layer calls go through `interfaces/` contracts.”

## Queue Consumer Architecture (Redis Workers)

### Queue model

Use **Redis Streams** with consumer groups for durability and replay:
- stream: `taskflow:queue:{env}:{tenant}` (or per-queue key by job type)
- consumer group: `taskflow:workers:{env}:{tenant}`

### Message types (typed commands/events)

Message commands:
- `JobStart` (create job run, enqueue workflow execution)
- `WorkflowExecute` (execute a workflow graph run)
- `WorkflowResume` (resume from checkpoint)
- `AgentRun` (run a CrewAI-based agent step, optional split)

Message events (optional; emitted for streaming & audit):
- `JobEvent` (token deltas, step transitions, tool calls)
- `JobCompleted`
- `JobFailed`

### Consumer loop

Each consumer has:
- decode message -> validate -> idempotency check -> execute handler -> checkpoint persist -> ack message
- on transient failure: retry/backoff
- on permanent failure: dead-letter -> record -> ack original to prevent poison-pill loops

### Idempotency strategy

Use an `idempotency_key` per message:
- store in Redis with TTL: `taskflow:idem:{key}`
- if already processed, ack and skip

This ensures safe retries without duplicating side effects (e.g., double checkpoint updates).

### Retry policy

Classify failures (via `errors/classifier.py`):
- retryable: timeouts, rate limits, temporary network failures, transient Redis errors
- non-retryable: invalid input/state, schema mismatches, unrecoverable persistence corruption

Backoff:
- exponential with jitter
- max attempts (e.g. 5-8)

After max attempts:
- publish to DLQ stream `taskflow:dlq:{...}`
- emit `JobFailed`/stream error event

## Workflow Engine Structure (LangGraph + Persistence)

### Execution modes

The workflow engine supports:
- `start(job_input)` -> create initial workflow state -> run graph -> stream events -> checkpoint -> finalize
- `resume(job_id, checkpoint_id)` -> load state -> continue graph -> checkpoint -> finalize

### LangGraph integration

Separate the **graph definition** from the **runner**:
- `workflows/graphs/graph_factory.py`: defines the LangGraph graph (nodes later)
- `workflows/engine/runner.py`: executes the graph, handles streaming and persistence

### State and checkpoints

Define a canonical workflow state:
- `job_id`
- `tenant_id`
- `workflow_version`
- `messages` (chat history summaries/refs)
- `artifact store references` (links/pointers, not full payloads)
- `current_step` / control-flow pointers
- `tool results` cache refs

Checkpoints:
- store intermediate state per step transition
- allow resume after worker restarts
- checkpoint identifiers returned in `JobEvent` and persisted for audit

### Streaming events from workflow

Workflow runner emits standardized events:
- `token_delta` (if model streaming)
- `step_started` / `step_completed`
- `tool_call_started` / `tool_call_completed`
- `checkpoint_saved`

These events are pushed to streaming layer (Redis streams/pubsub) so API clients can subscribe.

## Agent Orchestration Structure (CrewAI + Memory + LLM Router)

### Orchestration responsibilities

The agent orchestration layer:
- selects the crew/tasks strategy (later business logic)
- binds the LLM router to the CrewAI agents
- wires memory retrieval into the agent context builder
- transforms tool call results into a normalized format for workflow consumption
- emits streaming events (crew step transitions, tool calls, model deltas)

### Adapter style

Treat CrewAI and LiteLLM as pluggable adapters:
- `integrations/crewai/adapter.py` exposes an interface used by orchestration
- `integrations/litellm/router.py` exposes an interface used by agents

This keeps the “what model/tool is used” outside the orchestration glue.

## Shared Interfaces (Design Contracts)

Below are interface contracts (conceptual). Implementations live under `integrations/` and services under `workflows/` / `agents/`.

### 1. Queue
- `QueuePublisher.publish(command: QueueCommand) -> None`
- `QueueConsumer.consume_loop(handler_registry: HandlerRegistry) -> None`
- `QueueMessage` includes: `message_id`, `job_id`, `idempotency_key`, `attempt`, `tenant_id`, `payload`

### 2. LLM Router (LiteLLM)
- `LLMRouter.route(request: LLMRequest) -> LLMResultStream | LLMResult`
- `LLMRequest` includes: `tenant_id`, `model_policy`, `prompt/messages`, `tools_schema`, `stream: bool`
- `LLMResult` includes: `provider`, `model`, `content`, `usage` (tokens), `trace_id`

### 3. Memory Retrieval
- `MemoryRetriever.retrieve(query: MemoryQuery) -> MemoryContext`
- `MemoryContext` includes: snippets/doc ids, confidence scores, and optionally citations

### 4. Workflow Engine
- `WorkflowEngine.start(input: WorkflowStartInput) -> JobId`
- `WorkflowEngine.resume(job_id: str, checkpoint_id: str) -> JobId`
- `WorkflowEngine emits WorkflowEvent`s` (token deltas, step transitions, checkpoint_saved)

### 5. Persistence (workflow persistence)
- `WorkflowCheckpointStore.save(state: WorkflowState, metadata) -> checkpoint_id`
- `WorkflowCheckpointStore.load(job_id, checkpoint_id) -> WorkflowState`

### 6. Streaming Publisher
- `EventPublisher.publish(job_id: str, event: WorkflowEvent) -> None`
- Must support events emitted during the run and on failure.

### 7. Observability Hooks
- `ObservabilitySink.on_event(event: ObservabilityEvent) -> None`
- `ObservabilityEvent` includes: timestamps, category (queue/workflow/llm/memory), duration, counters, and correlation ids

## Logging Strategy (Structured Logging + Correlation)

### Structured logs (JSON)

Use JSON logs with consistent fields:
- `timestamp`
- `level`
- `service`: `ai-runtime`
- `env`
- `tenant_id`
- `job_id`
- `request_id` (API requests)
- `trace_id` (if tracing enabled)
- `event` (short machine-readable string)
- `message` (human-readable)
- `duration_ms` (for timed operations)
- `attempt` (for retries)
- `provider/model` (for LLM)
- `error_code` + `error_type` (on failures)

### Correlation

Generate correlation ids at API entry:
- `request_id` attached to the initial job command
- propagate into queue messages and workflow/agent events

For streaming:
- include `job_id` and `event_id` so clients can order events.

### Redaction policy

Ensure logs never include:
- API keys
- raw PII payloads

Only log:
- counts, sizes, hashes/correlation identifiers
- redacted snippets when debugging is explicitly enabled

## Error Handling Strategy

### Error taxonomy

Define categories:
- `ValidationError` (schema/input invalid)
- `ProviderError` (LLM provider failure)
- `TransientError` (timeouts, rate limits, temporary network/Redis issues)
- `PersistenceError` (checkpoint/DB/serialization issues)
- `WorkflowExecutionError` (graph node failure)
- `InternalError` (unexpected exceptions)

### Classification and retry rules

Use `errors/classifier.py`:
- If retryable -> throw `RetryableError` with `retry_after` hint
- If non-retryable -> `NonRetryableError`
- Persistence errors after partial checkpoint failures should be treated carefully:
  - persist a “failed_checkpoint” marker when safe
  - do not lose audit data

### API errors

FastAPI exceptions return consistent JSON:
- `error_code` (stable)
- `message` (user-safe)
- `details` (optional debug info gated by env)

For streaming endpoints:
- emit a terminal event `stream_error` containing `error_code`

### Queue errors

For each message:
- classify -> decide retry/DLQ
- on terminal failure: enqueue/publish `JobFailed` event and checkpoint failure info
- always ack the message after handling to avoid endless loops

### Poison pill prevention

If deserialization/contract validation fails:
- send to DLQ immediately
- ack original

## Observability Hooks (Where to Instrument)

Instrument these boundaries:
- `api` entry/exit for request timing and validation failures
- queue consume latency and handler duration
- checkpoint save/load duration
- LLM request/response:
  - latency
  - provider/model
  - token usage (if available)
- memory retrieval:
  - retrieval time
  - number of documents/snippets returned
- workflow step transitions:
  - step durations
  - number of tool calls

Hooks should be optional and off by default in local dev to keep noise low.

---

End of design document.

