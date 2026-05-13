from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ..base.contracts import AgentError, AgentOutputEnvelope, AgentStepSpec, AgentRunContext, AgentRole
from ..memory.workspace import AgentWorkspace
from ..output_validation.output_validator import OutputValidatorPort
from ..registry.agent_registry import AgentRegistry
from .ports import AuditLoggerPort, AgentEventEmitterPort, ConfidenceScoringPort, ToolCallExecutionPort


class AgentManagerResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agentOutputs: list[AgentOutputEnvelope]
    roleOutputsByRole: dict[AgentRole, dict[str, Any]] = Field(default_factory=dict)
    confidence: dict[str, Any] | None = None


class AgentManager:
    """
    Scalable multi-agent orchestration entrypoint.

    Workflow layer (LangGraph nodes) calls `execute()`; this module delegates:
    - role selection to `AgentRegistry`
    - prompt isolation to `PromptManager` (provided later)
    - tool schemas to `ToolRegistry` (provided later)
    - memory retrieval via a memory port (provided later)
    - structured output validation via `OutputValidatorPort`
    - agent execution via a CrewAI adapter (provided later)
    - retry decisions via retry policies (provided later)
    - observability + audit via ports

    No business logic implementation yet; methods include explicit structure and contracts.
    """

    def __init__(
        self,
        *,
        agentRegistry: AgentRegistry,
        outputValidator: OutputValidatorPort,
        eventEmitter: AgentEventEmitterPort,
        auditLogger: AuditLoggerPort,
        confidenceScoring: ConfidenceScoringPort,
        toolExecutor: ToolCallExecutionPort,
    ) -> None:
        self._agentRegistry = agentRegistry
        self._outputValidator = outputValidator
        self._eventEmitter = eventEmitter
        self._auditLogger = auditLogger
        self._confidenceScoring = confidenceScoring
        self._toolExecutor = toolExecutor

    async def execute(
        self,
        *,
        stepSpec: AgentStepSpec,
        workspace: AgentWorkspace,
        sharedContext: dict[str, Any] | None = None,
    ) -> AgentManagerResult:
        """
        Execution plan (design-only):
        1) Build `AgentRunContext` from workspace
        2) Select roles for `stepSpec` via `AgentRegistry`
        3) Construct isolated prompts per agent role (PromptManager later)
        4) Provide shared memory access (MemoryPort later) scoped by workspace constraints
        5) Execute roles as a crew (CrewAI adapter later)
        6) Validate structured outputs per role via `OutputValidatorPort`
        7) Compute/collect confidence via `ConfidenceScoringPort`
        8) Emit observability events at:
           - run start/end/fail
           - tool call start/end
           - output validation success/fail
        9) Write audit logs for:
           - run start
           - approval of outputs (if any)
           - failures with error codes
        10) Return normalized `AgentManagerResult`
        """
        raise NotImplementedError("AgentManager.execute: business logic not implemented yet")

