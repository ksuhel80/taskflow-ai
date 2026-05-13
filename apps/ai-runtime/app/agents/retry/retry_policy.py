from __future__ import annotations

from dataclasses import dataclass

from ..base.contracts import AgentError


@dataclass(frozen=True)
class AgentRetryPolicy:
    """
    Retry policy for bounded retries around tool calling / provider calls / output validation.

    The actual scheduling/backoff is implementation-specific and owned by the orchestration layer.
    """

    maxAttempts: int = 4
    baseBackoffMs: int = 250
    maxBackoffMs: int = 10_000
    jitterPct: float = 0.2

    retryCategories: set[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.retryCategories is None:
            object.__setattr__(
                self, "retryCategories", {"RETRYABLE", "VALIDATION"}  # default categories
            )


def should_retry(*, agentError: AgentError, retryPolicy: AgentRetryPolicy) -> bool:
    if not agentError.retryable:
        return False
    return agentError.category in retryPolicy.retryCategories

