from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Severity(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    FATAL = "fatal"


class TraceContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    traceId: str
    spanId: str | None = None
    requestId: str | None = None
    correlationId: str | None = None

    tenantId: str | None = None
    workspaceId: str | None = None
    workflowRunId: str | None = None
    agentRunId: str | None = None
    queueJobId: str | None = None


class LogEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ts: datetime = Field(default_factory=datetime.utcnow)
    severity: Severity = Severity.INFO
    event: str
    message: str
    context: TraceContext | None = None
    fields: dict[str, Any] = Field(default_factory=dict)


class AITelemetryEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ts: datetime = Field(default_factory=datetime.utcnow)
    eventType: str
    context: TraceContext
    modelProvider: str | None = None
    modelKey: str | None = None

    inputTokens: int | None = None
    outputTokens: int | None = None
    totalTokens: int | None = None
    costUsd: float | None = None
    latencyMs: int | None = None
    confidenceScore: float | None = None

    ok: bool = True
    errorCode: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class QueueTelemetryEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ts: datetime = Field(default_factory=datetime.utcnow)
    queueName: str
    jobName: str
    jobId: str | None = None
    status: str
    attempt: int | None = None
    durationMs: int | None = None
    lagMs: int | None = None
    context: TraceContext | None = None
    errorCode: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

