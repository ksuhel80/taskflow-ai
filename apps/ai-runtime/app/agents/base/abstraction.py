from __future__ import annotations

from typing import Protocol

from .contracts import AgentConfidence, AgentError, AgentOutputEnvelope, AgentRunContext, AgentStepSpec


class AgentLifecyclePort(Protocol):
    """
    Base interface for agent execution. Implementations are adapters around CrewAI or other agent runtimes.
    """

    async def execute_step(self, *, stepSpec: AgentStepSpec, context: AgentRunContext) -> AgentOutputEnvelope: ...


class ConfidenceScoringPort(Protocol):
    async def score(
        self,
        *,
        context: AgentRunContext,
        stepSpec: AgentStepSpec,
        output: AgentOutputEnvelope,
    ) -> AgentConfidence: ...


class AgentErrorClassifierPort(Protocol):
    async def classify(self, *, context: AgentRunContext, exc: Exception) -> AgentError: ...

