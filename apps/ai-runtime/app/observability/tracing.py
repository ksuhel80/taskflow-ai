from __future__ import annotations

from typing import Iterable

from .providers.base import TracingProvider
from .types import TraceContext


class TraceManager:
    """
    Coordinates one primary tracer plus optional secondary tracers.
    """

    def __init__(self, providers: Iterable[TracingProvider]) -> None:
        self._providers = list(providers)

    def start_span(self, *, name: str, context: TraceContext | None = None) -> TraceContext:
        active = context
        for p in self._providers:
            active = p.start_span(name=name, context=active)
        if active is None:
            raise RuntimeError("trace_provider_returned_none")
        return active

    def end_span(self, *, context: TraceContext, ok: bool = True, error_code: str | None = None) -> None:
        for p in reversed(self._providers):
            p.end_span(context=context, ok=ok, error_code=error_code)

