from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class WorkflowEventType(str, Enum):
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_RESUMED = "workflow_resumed"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    WORKFLOW_CANCELLED = "workflow_cancelled"

    STEP_STARTED = "step_started"
    STEP_COMPLETED = "step_completed"

    CHECKPOINT_SAVED = "checkpoint_saved"

    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_DECIDED = "approval_decided"

    RETRY_SCHEDULED = "retry_scheduled"
    ERROR_RECOVERED = "error_recovered"


class WorkflowEvent(BaseModel):
    """
    Streaming/audit event contract.

    Payload must be redacted-safe and JSON-serializable.
    """

    model_config = ConfigDict(extra="forbid")

    schemaVersion: str = "1"
    eventType: WorkflowEventType

    tenantId: str
    jobId: str
    workflowKey: str
    workflowVersion: str

    seq: int = 0
    checkpointSeq: int | None = None
    traceId: str | None = None

    payload: dict[str, Any] = Field(default_factory=dict)

    createdAt: datetime = Field(default_factory=datetime.utcnow)


class WorkflowEventTerminalPayload(BaseModel):
    """
    Standard payload fields for terminal events.
    """

    model_config = ConfigDict(extra="forbid")

    errorCode: str | None = None
    errorMessage: str | None = None
    retryable: bool | None = None

