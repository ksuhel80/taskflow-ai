from __future__ import annotations

from typing import Protocol

from ..types import AITelemetryEvent, LogEvent, QueueTelemetryEvent, TraceContext


class LoggerProvider(Protocol):
    def emit_log(self, event: LogEvent) -> None: ...


class TracingProvider(Protocol):
    def start_span(self, *, name: str, context: TraceContext | None = None) -> TraceContext: ...
    def end_span(self, *, context: TraceContext, ok: bool = True, error_code: str | None = None) -> None: ...


class TelemetryProvider(Protocol):
    def emit_ai_telemetry(self, event: AITelemetryEvent) -> None: ...
    def emit_queue_telemetry(self, event: QueueTelemetryEvent) -> None: ...


class AnalyticsProvider(Protocol):
    def track(self, *, event: str, distinct_id: str, properties: dict[str, object]) -> None: ...

