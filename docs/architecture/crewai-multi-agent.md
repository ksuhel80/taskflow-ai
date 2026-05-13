# TaskFlow AI - Scalable CrewAI Multi-Agent Architecture

This document designs a production-ready multi-agent system for `apps/ai-runtime` using **CrewAI**, optimized for:

- shared memory access with tenant safety
- isolated prompts per agent
- structured outputs
- tool calling
- agent-level observability + confidence scoring
- retries with bounded attempts
- workflow integration (LangGraph step layer)
- audit logging
- workspace isolation (job-scoped execution contexts)

Design constraint: no business logic yet. All agents run through contracts/adapters.

## 1) Responsibilities

### `agents/*` (orchestration + contracts)

- Define base agent abstraction and output contracts
- Provide agent registry (crew membership + step role mapping)
- Orchestrate tool calling via a tool registry
- Validate structured outputs
- Emit agent observability events and confidence scoring results
- Call shared memory retrieval via a memory interface
- Apply retry policy around tool/LLM calls
- Maintain workspace isolation per job (tenant/job-scoped context)

### `integrations/crewai/*` (CrewAI vendor adapter)

- Translate TaskFlow contracts into CrewAI constructs
- Execute CrewAI tasks/agents without leaking CrewAI types across the codebase

### `workflows/*` (LangGraph step layer)

- Calls `AgentManager` at “agent steps”
- Translates agent outputs into workflow state and streaming events

### `packages/database/*`

- Persists audit logs and workflow/agent run tracking (later via repositories)

## 2) Folder Structure (Proposed)

```txt
apps/ai-runtime/app/
  agents/
    base/
      abstraction.py                  # BaseAgent + lifecycle interface
      contracts.py                    # ToolCall/AgentOutput/Error contracts (types only)
    registry/
      agent_registry.py              # maps workflow step -> crew roles
    crew/
      crew_orchestrator.py          # builds/executes crew via CrewAI adapter (no CrewAI types)
    tools/
      tool_registry.py              # registers ToolSpecs and resolves invocations
      tool_contracts.py            # Tool input/output schemas + invocation contracts
    prompts/
      prompt_manager.py            # isolates prompts + renders templates per workspace
      templates/                   # system/user prompt templates per agent role
    memory/
      workspace.py                 # job-scoped workspace + shared memory retrieval binding
      memory_port.py              # MemoryRetriever interface used by agents
    output_validation/
      output_validator.py         # validates structured outputs from agents
    observability/
      events.py                    # Agent events for streaming/audit
      logging_strategy.py         # standardized agent logging fields + redaction rules
    retry/
      retry_policy.py             # retry policy + retryable error classification

  integrations/
    crewai/
      adapter.py                   # CrewAI adapter implementing an agent execution port
```

## 3) Shared Memory Access + Workspace Isolation

### Workspace isolation (job-scoped)

Each workflow run creates a `Workspace` containing:

- `workspaceId` (derived from `tenantId + jobId + workflowStepId`)
- `tenantId`, `jobId`
- `requestId` / `traceId` for correlation
- `memoryNamespaces` (which namespaces the agents are allowed to query)
- `promptVariables` (safe data only)
- tool execution context (workspace-specific constraints/timeouts)

### Shared memory (retrieval-only)

Agents can access shared memory through a `MemoryPort`:

- `retrieve(query) -> MemoryContext` (always tenant scoped)
- Retrieval is read-only from the agent layer perspective

## 4) Prompt Management (Isolated Prompts)

Each agent has:

- an immutable `system_prompt` per version
- a rendered `user_prompt` scoped to the workspace
- a strict separation between:
  - shared context (from memory + workflow state references)
  - isolated agent instructions (role-specific constraints)

Prompt rendering strategy:

- deterministic, JSON-serializable inputs
- versioned templates for auditability
- redaction-safe formatting (no secrets/PII in prompts unless explicitly allowed in dev)

## 5) Structured Outputs + Output Validation

All agents must emit:

- `AgentOutputEnvelope` containing:
  - `agentRole`
  - `schemaVersion`
  - `output` (typed structured payload)
  - `explainability` (optional, but required by some workflows)
  - `confidence` (optional if workflow performs scoring separately)
  - `llmUsage` (optional, for cost tracking)

Output validation:

- output is validated against a Pydantic model per agent role
- if validation fails:
  - classify as retryable vs non-retryable based on error type
  - emit `agent_output_validation_failed` event
  - optionally schedule a structured re-ask (later; not business logic yet)

## 6) Tool Calling System

Tool system is contract-first:

- `ToolSpec` defines:
  - `name`
  - `inputSchema`
  - `outputSchema`
  - `capabilities` / access control metadata
- A `ToolRegistry` resolves tool invocations by name.

Agents request tool calls via structured tool invocation records.
The actual tool execution is performed via a tool executor port (later), but:

- the registry validates schemas before executing
- tool results are normalized back into structured events

## 7) Agent Observability + Confidence Scoring

Agent events emitted:

- `agent_run_started`
- `agent_run_completed`
- `agent_run_failed`
- `agent_step_started`
- `agent_output_validated`
- `agent_tool_call_started`
- `agent_tool_call_completed`
- `agent_confidence_computed`

Confidence scoring contract:

- `confidenceScore: float` (0..1)
- `rationale: str`
- `signals: dict` (optional)
- if confidence is computed by a separate step agent, the output should still follow the same contract.

## 8) Retry Logic and Error Handling

Retry policy scope:

- LLM/provider timeouts
- transient tool failures (network/5xx)
- output validation failures if deemed “recoverable” by re-asking (later)

Classification:

- retryable -> bounded attempts with exponential backoff + jitter
- non-retryable -> terminal failure -> workflow step fails and triggers LangGraph recovery

## 9) Workflow Integration

Workflow steps (LangGraph nodes) call:

- `AgentManager.execute(stepSpec, workspace, workflowStateRefs)`

`AgentManager` returns:

- normalized structured outputs per role
- tool call summaries
- confidence score and explainability payloads
- event stream records for SSE/audit

## Engineering Guidelines

1. CrewAI vendor types never leak into `agents/*` public contracts.
2. All prompt templates and output schemas are versioned.
3. Every agent action must be tenant scoped.
4. Every agent emits structured observability events.
5. Output validation is mandatory; never assume the LLM is well-formed.
6. Always implement bounded retries with idempotent tool calling later.

---

End of design.
