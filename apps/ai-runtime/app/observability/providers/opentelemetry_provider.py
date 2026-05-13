from __future__ import annotations

import uuid

from ..types import TraceContext


class OpenTelemetryProvider:
    """
    OpenTelemetry adapter scaffold.

    Real implementation should:
    - initialize tracer provider
    - export traces/metrics/logs (OTLP)
    - propagate W3C trace context across API, queue, and workflow boundaries
    """

    def start_span(self, *, name: str, context: TraceContext | None = None) -> TraceContext:
        if context:
            return context
        return TraceContext(traceId=uuid.uuid4().hex, spanId=uuid.uuid4().hex[:16], correlationId=name)

    def end_span(self, *, context: TraceContext, ok: bool = True, error_code: str | None = None) -> None:
        return

