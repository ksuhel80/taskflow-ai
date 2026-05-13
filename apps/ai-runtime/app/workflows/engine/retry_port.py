from __future__ import annotations

from enum import Enum
from typing import Any, Protocol

from ..state.types import WorkflowError, WorkflowErrorCategory


class RetryDecision(str, Enum):
    RETRY = "RETRY"
    NO_RETRY = "NO_RETRY"
    DLQ = "DLQ"


class RetryPolicy:
    """
    Retry policy inputs.

    This is a data model; the workflow engine will use it to decide behavior.
    """

    def __init__(
        self,
        *,
        maxAttempts: int = 5,
        baseBackoffMs: int = 500,
        maxBackoffMs: int = 10_000,
        jitterPct: float = 0.2,
        retryOnCategories: set[WorkflowErrorCategory] | None = None,
    ) -> None:
        self.maxAttempts = maxAttempts
        self.baseBackoffMs = baseBackoffMs
        self.maxBackoffMs = maxBackoffMs
        self.jitterPct = jitterPct
        self.retryOnCategories = retryOnCategories or {WorkflowErrorCategory.TRANSIENT, WorkflowErrorCategory.PROVIDER}


class ErrorClassifierPort(Protocol):
    """
    Maps exceptions to a WorkflowError and decides retry behavior.
    """

    def classify(self, *, exc: Exception) -> tuple[WorkflowError, RetryDecision, dict[str, Any]]: ...

