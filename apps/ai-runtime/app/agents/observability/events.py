from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ..base.contracts import AgentConfidence, AgentError, LLMUsage, AgentRole


class AgentEventType(str, Enum):
    AGENT_RUN_STARTED = "agent_run_started"
    AGENT_RUN_COMPLETED = "agent_run_completed"
    AGENT_RUN_FAILED = "agent_run_failed"

    AGENT_STEP_STARTED = "agent_step_started"
    AGENT_STEP_COMPLETED = "agent_step_completed"

    AGENT_TOOL_CALL_STARTED = "agent_tool_call_started"
    AGENT_TOOL_CALL_COMPLETED = "agent_tool_call_completed"
    AGENT_TOOL_CALL_FAILED = "agent_tool_call_failed"

    AGENT_OUTPUT_VALIDATED = "agent_output_validated"
    AGENT_CONFIDENCE_COMPUTED = "agent_confidence_computed"


class AgentEventEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schemaVersion: str = "1"
    eventType: AgentEventType

    tenantId: str
    jobId: str
    workflowKey: str
    workflowVersion: str

    workspaceId: str | None = None
    agentRole: AgentRole | None = None
    stepId: str | None = None

    requestId: str | None = None
    traceId: str | None = None

    seq: int = 0
    createdAt: datetime = Field(default_factory=datetime.utcnow)

    payload: dict[str, Any] = Field(default_factory=dict)


class AgentRunFailurePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    error: AgentError
    llmUsage: LLMUsage | None = None


class AgentConfidencePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    confidence: AgentConfidence

