from __future__ import annotations

from typing import Iterable

from .providers.base import LoggerProvider
from .types import LogEvent


class ObservabilityLogger:
    """
    Fan-out logger for structured security/runtime logs.
    """

    def __init__(self, providers: Iterable[LoggerProvider]) -> None:
        self._providers = list(providers)

    def emit(self, event: LogEvent) -> None:
        for p in self._providers:
            p.emit_log(event)

