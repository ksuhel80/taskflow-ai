from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ToolSpec(BaseModel):
    """
    Tool contract definition (schema-first).

    Implementation is intentionally out of scope (no business logic).
    """

    name: str
    description: str
    inputSchema: dict[str, Any]
    outputSchema: dict[str, Any]

    model_config = ConfigDict(extra="forbid")


class ToolCall(BaseModel):
    toolName: str
    toolCallId: str
    args: dict[str, Any]
    createdAt: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(extra="forbid")


class ToolResult(BaseModel):
    toolName: str
    toolCallId: str

    ok: bool
    result: dict[str, Any] | None = None
    error: dict[str, Any] | None = None

    model_config = ConfigDict(extra="forbid")


class ToolCapability(BaseModel):
    """
    Tool access control metadata (workspace isolation).
    """

    # Namespaces the tool is allowed to access.
    allowedMemoryNamespaces: list[str] = []
    # Optional capability tags for routing.
    tags: list[str] = []

    model_config = ConfigDict(extra="forbid")


class ToolExecutionError(BaseModel):
    code: str
    category: Literal["VALIDATION", "RETRYABLE", "NON_RETRYABLE", "INTERNAL"]
    message: str
    details: dict[str, Any] | None = None

    model_config = ConfigDict(extra="forbid")

