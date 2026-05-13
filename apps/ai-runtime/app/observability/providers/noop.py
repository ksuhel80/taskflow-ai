from __future__ import annotations

from ..types import AITelemetryEvent, LogEvent, QueueTelemetryEvent, TraceContext


class NoopProvider:
    def emit_log(self, event: LogEvent) -> None:
        return

    def start_span(self, *, name: str, context: TraceContext | None = None) -> TraceContext:
        return context or TraceContext(traceId=f"noop-{name}")

    def end_span(self, *, context: TraceContext, ok: bool = True, error_code: str | None = None) -> None:
        return

    def emit_ai_telemetry(self, event: AITelemetryEvent) -> None:
        return

    def emit_queue_telemetry(self, event: QueueTelemetryEvent) -> None:
        return

    def track(self, *, event: str, distinct_id: str, properties: dict[str, object]) -> None:
        return

