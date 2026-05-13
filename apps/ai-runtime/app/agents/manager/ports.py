from __future__ import annotations

from typing import Any, Protocol

from ..base.contracts import AgentOutputEnvelope, AgentStepSpec, AgentRunContext, AgentError
from ..observability.events import AgentEventEnvelope
from ..memory.workspace import AgentWorkspace


class AgentEventEmitterPort(Protocol):
    async def emit(self, event: AgentEventEnvelope) -> None: ...


class AuditLoggerPort(Protocol):
    async def log_audit_event(
        self,
        *,
        tenantId: str,
        jobId: str,
        workflowKey: str,
        workflowVersion: str,
        eventType: str,
        payload: dict[str, Any] | None,
    ) -> None: ...


class ToolCallExecutionPort(Protocol):
    async def execute_tool_call(self, *, toolName: str, args: dict[str, Any]) -> dict[str, Any]: ...


class ConfidenceScoringPort(Protocol):
    async def score_confidence(
        self,
        *,
        context: AgentRunContext,
        stepSpec: AgentStepSpec,
        agentOutputs: list[AgentOutputEnvelope],
    ) -> dict[str, Any]: ...

