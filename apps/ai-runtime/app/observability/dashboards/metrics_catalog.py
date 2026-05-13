from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MetricDef:
    key: str
    description: str
    unit: str
    source: str


AI_METRICS = [
    MetricDef(
        key="ai.cost.total_usd",
        description="Total AI spend in USD.",
        unit="usd",
        source="AICostUsage",
    ),
    MetricDef(
        key="ai.tokens.input_total",
        description="Total input tokens.",
        unit="tokens",
        source="AICostUsage",
    ),
    MetricDef(
        key="ai.tokens.output_total",
        description="Total output tokens.",
        unit="tokens",
        source="AICostUsage",
    ),
    MetricDef(
        key="ai.latency.p95_ms",
        description="P95 AI operation latency.",
        unit="ms",
        source="AICostUsage",
    ),
    MetricDef(
        key="ai.confidence.avg",
        description="Average confidence score for AI outputs.",
        unit="ratio",
        source="AIConfidenceScore",
    ),
    MetricDef(
        key="ai.failures.rate",
        description="AI operation failure rate.",
        unit="ratio",
        source="AITelemetryEvent",
    ),
]

QUEUE_METRICS = [
    MetricDef(
        key="queue.lag.ms",
        description="Queue lag in milliseconds.",
        unit="ms",
        source="QueueTelemetryEvent",
    ),
    MetricDef(
        key="queue.jobs.failed",
        description="Failed jobs count by queue/job type.",
        unit="count",
        source="QueueTelemetryEvent",
    ),
    MetricDef(
        key="queue.jobs.retry_count",
        description="Retried jobs count.",
        unit="count",
        source="QueueTelemetryEvent",
    ),
]

