from __future__ import annotations

from datetime import datetime

from .ai_telemetry import AITelemetry
from .types import QueueTelemetryEvent, TraceContext


class QueueMonitor:
    """
    Queue monitoring hooks for workers/processors.
    """

    def __init__(self, telemetry: AITelemetry) -> None:
        self._telemetry = telemetry

    def on_job_started(
        self,
        *,
        queueName: str,
        jobName: str,
        jobId: str,
        attempt: int,
        context: TraceContext | None = None,
    ) -> None:
        self._telemetry.emit_queue(
            QueueTelemetryEvent(
                ts=datetime.utcnow(),
                queueName=queueName,
                jobName=jobName,
                jobId=jobId,
                status="started",
                attempt=attempt,
                context=context,
            )
        )

    def on_job_completed(
        self,
        *,
        queueName: str,
        jobName: str,
        jobId: str,
        durationMs: int,
        attempt: int,
        context: TraceContext | None = None,
    ) -> None:
        self._telemetry.emit_queue(
            QueueTelemetryEvent(
                queueName=queueName,
                jobName=jobName,
                jobId=jobId,
                status="completed",
                durationMs=durationMs,
                attempt=attempt,
                context=context,
            )
        )

    def on_job_failed(
        self,
        *,
        queueName: str,
        jobName: str,
        jobId: str,
        durationMs: int | None,
        attempt: int,
        errorCode: str,
        context: TraceContext | None = None,
    ) -> None:
        self._telemetry.emit_queue(
            QueueTelemetryEvent(
                queueName=queueName,
                jobName=jobName,
                jobId=jobId,
                status="failed",
                durationMs=durationMs,
                attempt=attempt,
                errorCode=errorCode,
                context=context,
            )
        )

