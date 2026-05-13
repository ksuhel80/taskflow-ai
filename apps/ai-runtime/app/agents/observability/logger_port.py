from __future__ import annotations

from typing import Any, Protocol

from .logging_strategy import AgentLogFields


class StructuredAgentLoggerPort(Protocol):
    """
    Contract for JSON structured logging for agent execution.

    Implementations should:
    - attach AgentLogFields
    - redact secrets/PII
    - emit logs at appropriate severity levels
    """

    def log(self, *, fields: AgentLogFields, event: str, message: str, extra: dict[str, Any] | None = None) -> None: ...

