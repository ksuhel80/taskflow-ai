from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


AgentRole = Literal["researcher", "planner", "reviewer", "scrum_master"]


class LLMUsage(BaseModel):
    provider: str
    model: str
    promptTokens: int | None = None
    completionTokens: int | None = None
    totalTokens: int | None = None
    costUsd: float | None = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(extra="forbid")


class AgentConfidence(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    rationale: str
    signals: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="forbid")


class AgentError(BaseModel):
    code: str
    category: Literal[
        "VALIDATION",
        "RETRYABLE",
        "NON_RETRYABLE",
        "TOOL",
        "PROVIDER",
        "INTERNAL",
    ]
    message: str
    details: dict[str, Any] | None = None
    retryable: bool

    model_config = ConfigDict(extra="forbid")


class ToolCallRequest(BaseModel):
    toolName: str
    toolCallId: str
    args: dict[str, Any]

    model_config = ConfigDict(extra="forbid")


class ToolCallResult(BaseModel):
    toolName: str
    toolCallId: str
    ok: bool
    result: dict[str, Any] | None = None
    error: dict[str, Any] | None = None

    model_config = ConfigDict(extra="forbid")


class AgentOutputEnvelope(BaseModel):
    """
    Structured agent output contract.
    """

    agentRole: AgentRole
    schemaVersion: str = "1"
    output: dict[str, Any]

    # Optional cross-cutting metadata:
    explainability: dict[str, Any] | None = None
    confidence: AgentConfidence | None = None
    llmUsage: LLMUsage | None = None

    model_config = ConfigDict(extra="forbid")


class AgentRunContext(BaseModel):
    """
    Minimal execution context passed to agents.
    """

    tenantId: str
    jobId: str
    workflowKey: str
    workflowVersion: str
    workspaceId: str

    requestId: str | None = None
    traceId: str | None = None

    model_config = ConfigDict(extra="forbid")


class AgentStepSpec(BaseModel):
    """
    Describes what the workflow step requires from the crew.
    """

    stepId: str
    stepSeq: int | None = None
    requiresHumanApproval: bool = False
    inputRef: str | None = None

    model_config = ConfigDict(extra="forbid")

