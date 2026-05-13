from __future__ import annotations

"""
Structured logging strategy for agent execution (design-only).

This module provides a contract and conventions; it does not implement log writing.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentLogFields:
    tenantId: str
    jobId: str
    workflowKey: str
    workflowVersion: str
    workspaceId: str | None = None
    agentRole: str | None = None
    stepId: str | None = None
    requestId: str | None = None
    traceId: str | None = None
    attempt: int | None = None

