from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ..events.emitter import WorkflowEventEmitterPort
from ..state.types import (
    ApprovalDecision,
    ApprovalRequest,
    RetryState,
    WorkflowCheckpoint,
    WorkflowError,
    WorkflowRunStatus,
    WorkflowState,
)
from .approvals_port import ApprovalDecisionPort, ApprovalPort
from .error_recovery import ErrorRecoveryPlan
from .persistence_port import WorkflowPersistencePort
from .retry_port import ErrorClassifierPort, RetryDecision, RetryPolicy


class WorkflowStartInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenantId: str
    jobId: str
    workflowKey: str
    workflowVersion: str

    # Redacted/safe reference or hash of input payload. Actual payload can be stored elsewhere later.
    inputRef: str | None = None
    inputPayload: dict[str, Any] = Field(default_factory=dict)

    requestId: str | None = None
    traceId: str | None = None


class WorkflowResumeInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenantId: str
    jobId: str
    workflowKey: str
    workflowVersion: str

    checkpointId: str
    # If resuming due to approval, provide the decision payload.
    approvalDecision: ApprovalDecision | None = None


class CancelInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenantId: str
    jobId: str
    reason: str | None = None


class WorkflowStartResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    jobId: str
    status: WorkflowRunStatus
    checkpointId: str | None = None


class WorkflowResumeResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    jobId: str
    status: WorkflowRunStatus
    checkpointId: str | None = None


class CancelResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    jobId: str
    status: WorkflowRunStatus = WorkflowRunStatus.CANCELLED


class WorkflowEngine:
    """
    LangGraph workflow engine (architecture-only scaffolding).

    This class coordinates:
    - state init/load
    - LangGraph execution (graph logic not implemented here)
    - checkpoint persistence
    - retry + error recovery classification
    - human approval pause/resume
    - streaming event emission
    - cancellation handling
    """

    def __init__(
        self,
        *,
        persistence: WorkflowPersistencePort,
        eventEmitter: WorkflowEventEmitterPort,
        retryPolicy: RetryPolicy,
        errorClassifier: ErrorClassifierPort,
        approvalPort: ApprovalPort | None = None,
    ) -> None:
        self._persistence = persistence
        self._eventEmitter = eventEmitter
        self._retryPolicy = retryPolicy
        self._errorClassifier = errorClassifier
        self._approvalPort = approvalPort

    def start(self, cmd: WorkflowStartInput) -> WorkflowStartResult:
        # Design intent (no business logic yet):
        # 1) Create/Load workflow run record (idempotent)
        # 2) Initialize WorkflowState with RetryState and identity fields
        # 3) Emit workflow_started
        # 4) Build LangGraph graph from WorkflowRegistry (separate module)
        # 5) Run graph with step boundary checkpoint callbacks
        # 6) Pause for approval nodes if encountered
        # 7) On completion: update run status + emit workflow_completed terminal event
        raise NotImplementedError("WorkflowEngine.start: business logic not implemented yet")

    def resume(self, cmd: WorkflowResumeInput) -> WorkflowResumeResult:
        # Design intent:
        # 1) Load checkpoint via persistence port
        # 2) Validate checkpointSeq/stateHash compatibility (optimistic concurrency later)
        # 3) If approvalDecision is provided, update state/approval records
        # 4) Continue LangGraph from checkpoint
        # 5) Persist checkpoints + emit events at step boundaries
        raise NotImplementedError("WorkflowEngine.resume: business logic not implemented yet")

    def cancel(self, cmd: CancelInput) -> CancelResult:
        # Design intent:
        # 1) Update workflow run status to CANCELLED in persistence
        # 2) Persist a cancellation checkpoint (optional depending on step boundary)
        # 3) Emit workflow_cancelled terminal event
        raise NotImplementedError("WorkflowEngine.cancel: business logic not implemented yet")

    # Internal helper hooks (still design-only; implement later)
    def _classify_error(self, exc: Exception) -> tuple[WorkflowError, RetryDecision, dict[str, Any]]:
        return self._errorClassifier.classify(exc=exc)

    def _plan_recovery(self, *, error: WorkflowError) -> ErrorRecoveryPlan:
        # This is intentionally a placeholder: recovery should be fully defined
        # alongside step boundary semantics and retry policy.
        return ErrorRecoveryPlan(
            error=error,
            retryAfterMs=None,
            nextAction="FAIL_RUN",
            metadata={},
        )

