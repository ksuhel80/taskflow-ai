from __future__ import annotations

from abc import ABC, abstractmethod

from .contracts import AgentOutputEnvelope, AgentRunContext, AgentStepSpec


class BaseAgent(ABC):
    """
    Base agent abstraction.

    Implementations wrap a specific execution runtime (CrewAI agent, tools, etc.).
    """

    roleName: str
    schemaVersion: str = "1"

    @abstractmethod
    async def run(
        self,
        *,
        stepSpec: AgentStepSpec,
        context: AgentRunContext,
    ) -> AgentOutputEnvelope:
        raise NotImplementedError

