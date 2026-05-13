from __future__ import annotations

from typing import Iterable

from .providers.base import AnalyticsProvider, TelemetryProvider
from .types import AITelemetryEvent, QueueTelemetryEvent


class AITelemetry:
    """
    Emits AI telemetry to telemetry sinks and product analytics.
    """

    def __init__(
        self,
        *,
        telemetryProviders: Iterable[TelemetryProvider],
        analyticsProviders: Iterable[AnalyticsProvider] = (),
    ) -> None:
        self._telemetry = list(telemetryProviders)
        self._analytics = list(analyticsProviders)

    def emit_ai(self, event: AITelemetryEvent) -> None:
        for t in self._telemetry:
            t.emit_ai_telemetry(event)

        # Product analytics (sample mapping)
        distinct = event.context.tenantId or "unknown_tenant"
        for a in self._analytics:
            a.track(
                event="ai.telemetry",
                distinct_id=distinct,
                properties={
                    "event_type": event.eventType,
                    "model_provider": event.modelProvider,
                    "model_key": event.modelKey,
                    "cost_usd": event.costUsd,
                    "latency_ms": event.latencyMs,
                    "ok": event.ok,
                },
            )

    def emit_queue(self, event: QueueTelemetryEvent) -> None:
        for t in self._telemetry:
            t.emit_queue_telemetry(event)

