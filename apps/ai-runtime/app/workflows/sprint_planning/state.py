from __future__ import annotations

from typing import Any, Literal, NotRequired
from typing_extensions import TypedDict


class LLMUsage(TypedDict, total=False):
    provider: str
    model: str
    promptTokens: int
    completionTokens: int
    totalTokens: int
    costUsd: float


class Explainability(TypedDict, total=False):
    agent: str
    rationale: str
    assumptions: list[str]
    references: NotRequired[list[str]]


class HumanApproval(TypedDict, total=False):
    approvalId: str
    stepId: str
    requestedAtIso: str
    summary: str

    status: Literal["PENDING", "APPROVED", "REJECTED"] | None
    decision: Literal["APPROVED", "REJECTED"] | None
    decidedAtIso: str | None
    decidedBy: str | None
    decisionReason: str | None


class RetryMeta(TypedDict, total=False):
    attempt: int
    maxAttempts: int
    lastErrorCode: str | None
    lastErrorCategory: str | None


class SprintContext(TypedDict, total=False):
    sprintGoal: str
    sprintStartIso: str
    sprintEndIso: str

    # History/backlog inputs are represented as references/pointers
    historyRef: str | None
    backlogRef: str | None

    # Additional context passed from web/API
    participants: list[str] | None
    constraints: dict[str, Any] | None


class ResearcherOutput(TypedDict, total=False):
    summary: str
    keyFindings: list[str]
    risksAndDependencies: list[str]
    explainability: Explainability
    llmUsage: LLMUsage | None


class PlannerOutput(TypedDict, total=False):
    allocation: dict[str, Any]
    capacityAssumptions: dict[str, Any]
    explainability: Explainability
    llmUsage: LLMUsage | None


class ReviewerOutput(TypedDict, total=False):
    workloadBalanceOk: bool
    issues: list[str]
    recommendations: list[str]
    explainability: Explainability
    llmUsage: LLMUsage | None


class ConfidenceOutput(TypedDict, total=False):
    score: float
    rationale: str
    llmUsage: LLMUsage | None


class SprintCommitPayload(TypedDict, total=False):
    sprintId: str
    allocation: dict[str, Any]
    confidenceScore: float
    artifacts: dict[str, Any]


class WorkflowError(TypedDict, total=False):
    errorCode: str
    errorCategory: str
    message: str
    details: dict[str, Any] | None


class SprintPlanningState(TypedDict, total=False):
    """
    Typed LangGraph state.

    All fields must be JSON-serializable.
    """

    # Identity + correlation
    tenantId: str
    jobId: str
    workflowKey: Literal["sprint_planning"]
    workflowVersion: str

    requestId: str | None
    traceId: str | None

    # Control
    status: Literal[
        "PENDING",
        "RUNNING",
        "PAUSED_FOR_APPROVAL",
        "COMPLETED",
        "FAILED",
        "CANCELLED",
    ]
    cancelRequested: bool
    cancelReason: str | None

    # Retry/error
    retry: RetryMeta
    error: WorkflowError | None

    # Human-in-the-loop approval
    approval: HumanApproval

    # Domain
    context: SprintContext
    researcher: ResearcherOutput
    planner: PlannerOutput
    reviewer: ReviewerOutput
    confidence: ConfidenceOutput
    commit: SprintCommitPayload

    # Streaming-friendly ledger
    explainabilityLog: list[Explainability]
    costLedger: list[LLMUsage]

    # Convenience sequencing for UI/events
    step: str | None
    stepSeq: int

