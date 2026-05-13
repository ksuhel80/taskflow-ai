from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class WorkflowRunStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PAUSED_FOR_APPROVAL = "PAUSED_FOR_APPROVAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class WorkflowErrorCategory(str, Enum):
    VALIDATION = "VALIDATION"
    PROVIDER = "PROVIDER"
    TRANSIENT = "TRANSIENT"
    PERSISTENCE = "PERSISTENCE"
    WORKFLOW_EXECUTION = "WORKFLOW_EXECUTION"
    INTERNAL = "INTERNAL"


class WorkflowError(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    category: WorkflowErrorCategory
    message: str
    retryable: bool = False
    details: dict[str, Any] | None = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)


class RetryState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    attempt: int = 0
    maxAttempts: int
    lastErrorCode: str | None = None
    lastErrorCategory: WorkflowErrorCategory | None = None


class ApprovalRequest(BaseModel):
    """
    Human approval checkpoint contract.

    This model is stored inside WorkflowState and checkpointed to allow deterministic pause/resume.
    """

    model_config = ConfigDict(extra="forbid")

    approvalId: str
    stepId: str
    approverRole: str

    # Redacted-safe summary of what requires approval (avoid storing secrets/raw PII).
    summary: str

    status: ApprovalStatus = ApprovalStatus.PENDING
    requestedAt: datetime = Field(default_factory=datetime.utcnow)

    decidedAt: datetime | None = None
    approvedBy: str | None = None
    decisionReason: str | None = None

    # When approved/rejected, the engine will update WorkflowState based on decision payload later.


class ApprovalDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    approvalId: str
    decision: Literal["APPROVED", "REJECTED"]
    decidedBy: str
    decisionReason: str | None = None
    decidedAt: datetime = Field(default_factory=datetime.utcnow)


class WorkflowState(BaseModel):
    """
    Canonical, JSON-serializable workflow state persisted for resume.

    Keep this model deterministic and forward-compatible; avoid storing secrets in state.
    """

    model_config = ConfigDict(extra="forbid")

    # Identity + correlation
    tenantId: str
    jobId: str
    workflowKey: str
    workflowVersion: str

    requestId: str | None = None
    traceId: str | None = None

    # Lifecycle
    status: WorkflowRunStatus = WorkflowRunStatus.PENDING
    currentStepId: str | None = None
    cancelledAt: datetime | None = None
    cancelReason: str | None = None

    startedAt: datetime | None = None
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    # Retry
    retry: RetryState

    # Human approvals
    approvals: list[ApprovalRequest] = Field(default_factory=list)

    # Domain data references (placeholders for later features)
    inputRef: str | None = None
    artifacts: dict[str, Any] = Field(default_factory=dict)
    agentCollaboration: dict[str, Any] = Field(default_factory=dict)
    memoryContext: dict[str, Any] = Field(default_factory=dict)

    # Error info
    error: WorkflowError | None = None

    def touch(self) -> None:
        self.updatedAt = datetime.utcnow()


class WorkflowCheckpoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    checkpointId: str
    checkpointSeq: int
    status: WorkflowRunStatus

    # Deterministic state for resume.
    state: WorkflowState

    # Integrity + idempotency aid.
    stateHash: str
    createdAt: datetime = Field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class WorkflowStepBoundary:
    """
    Identifies deterministic boundaries for checkpointing.

    LangGraph nodes should map to stable step boundaries that preserve resume semantics across versions.
    """

    stepId: str
    checkpointSeqIncrement: int = 1

