from __future__ import annotations

from typing import Any

from ..state.types import WorkflowError


class ErrorRecoveryPlan:
    """
    Design-only representation of what recovery should do for a given failure.

    The workflow runner uses this plan with retry/cancellation policies.
    """

    def __init__(
        self,
        *,
        error: WorkflowError,
        retryAfterMs: int | None,
        nextAction: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.error = error
        self.retryAfterMs = retryAfterMs
        self.nextAction = nextAction  # e.g. "RETRY_STEP", "RESUME_FROM_CHECKPOINT", "FAIL_RUN", "DLQ"
        self.metadata = metadata or {}

