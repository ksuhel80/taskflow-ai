from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AgentWorkspace:
    """
    Job-scoped workspace isolation.

    Agents may only access:
    - memory namespaces included in `allowedMemoryNamespaces`
    - safe prompt variables included in `promptVariables`
    - tool execution constraints defined for the workspace
    """

    tenantId: str
    jobId: str
    workflowKey: str
    workflowVersion: str
    workspaceId: str

    allowedMemoryNamespaces: list[str] = field(default_factory=list)
    promptVariables: dict[str, Any] = field(default_factory=dict)
    toolConstraints: dict[str, Any] = field(default_factory=dict)

    requestId: str | None = None
    traceId: str | None = None

