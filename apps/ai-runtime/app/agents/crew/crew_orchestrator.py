from __future__ import annotations

from typing import Any, Protocol

from ..base.contracts import AgentOutputEnvelope, AgentRole, AgentStepSpec, AgentRunContext
from ..memory.workspace import AgentWorkspace


class CrewAIExecutionPort(Protocol):
    """
    Vendor adapter interface for executing one or more agent roles via CrewAI.
    """

    async def run_roles(
        self,
        *,
        roles: list[AgentRole],
        stepSpec: AgentStepSpec,
        context: AgentRunContext,
        workspace: AgentWorkspace,
        isolatedPrompts: dict[AgentRole, dict[str, str]],
        toolPlan: list[dict[str, Any]],
    ) -> list[AgentOutputEnvelope]: ...


class CrewOrchestrator:
    """
    Multi-agent orchestration entrypoint (architecture-only).

    Responsibilities:
    - Execute selected roles via CrewAI adapter
    - Normalize adapter outputs into TaskFlow agent output envelopes
    - Provide hooks for:
      - retries
      - structured output validation
      - audit/log emission
    """

    def __init__(self, *, crewAI: CrewAIExecutionPort) -> None:
        self._crewAI = crewAI

    async def run(
        self,
        *,
        roles: list[AgentRole],
        stepSpec: AgentStepSpec,
        context: AgentRunContext,
        workspace: AgentWorkspace,
        isolatedPrompts: dict[AgentRole, dict[str, str]],
        toolPlan: list[dict[str, Any]],
    ) -> list[AgentOutputEnvelope]:
        return await self._crewAI.run_roles(
            roles=roles,
            stepSpec=stepSpec,
            context=context,
            workspace=workspace,
            isolatedPrompts=isolatedPrompts,
            toolPlan=toolPlan,
        )

