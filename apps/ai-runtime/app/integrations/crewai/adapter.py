from __future__ import annotations

from typing import Any, Protocol

from ...agents.base.contracts import AgentOutputEnvelope, AgentRole, AgentRunContext, AgentStepSpec
from ...agents.memory.workspace import AgentWorkspace


class CrewAIAdapterPort(Protocol):
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


class CrewAIAdapter(CrewAIAdapterPort):
    """
    CrewAI vendor adapter (stub).

    All CrewAI SDK interactions should remain in this module to preserve boundaries.
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
    ) -> list[AgentOutputEnvelope]:
        # Design-only:
        # - Map roles to CrewAI agent definitions
        # - Configure isolated system/user prompts per role
        # - Provide tool specs and tool calling hooks
        # - Enforce structured output parsing + JSON schema validation
        # - Stream intermediate steps/events via observability hooks later
        raise NotImplementedError("CrewAIAdapter.run_roles: business logic not implemented yet")

