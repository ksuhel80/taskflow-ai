from __future__ import annotations

from typing import Any

from ...base.agent import BaseAgent
from ...base.contracts import AgentOutputEnvelope, AgentRunContext, AgentStepSpec
from ...memory.memory_port import MemoryQuery, MemoryRetrieverPort
from ...memory.workspace import AgentWorkspace
from ...observability.events import AgentEventEnvelope, AgentEventType
from ...tools.tool_registry import ToolRegistry
from ...prompts.prompt_manager import PromptManager
from .output_schemas import (
    Blocker,
    Confidence,
    Explainability,
    IdleNudge,
    RiskEscalation,
    ScrumMasterOutput,
    SlackAction,
    SlackTarget,
    SprintSummary,
    StandupItem,
    StandupReport,
)


class ScrumMasterAgent(BaseAgent):
    roleName = "scrum_master"

    def __init__(
        self,
        *,
        promptManager: PromptManager,
        toolRegistry: ToolRegistry,
        memory: MemoryRetrieverPort,
        eventEmitter: Any | None = None,
    ) -> None:
        self._promptManager = promptManager
        self._toolRegistry = toolRegistry
        self._memory = memory
        self._eventEmitter = eventEmitter  # AgentEventEmitterPort-like (kept Any to avoid circulars)

    async def run(
        self,
        *,
        stepSpec: AgentStepSpec,
        context: AgentRunContext,
    ) -> AgentOutputEnvelope:
        """
        Implementation notes:
        - This agent is implemented as a deterministic orchestrator for now (no LLM calls yet).
        - It is fully wired for memory retrieval, tool hooks, structured output, confidence, and observability.
        - Later, CrewAI/LiteLLM execution can replace the deterministic core while preserving contracts.
        """

        await self._emit(
            context=context,
            stepId=stepSpec.stepId,
            eventType=AgentEventType.AGENT_RUN_STARTED,
            payload={"role": self.roleName},
        )

        # Memory retrieval (tenant scoped).
        mem = await self._memory.retrieve(
            query=MemoryQuery(
                tenantId=context.tenantId,
                namespaceType="WORKFLOW",
                namespaceKey=context.workflowKey,
                queryText="latest standup status, blockers, idle signals, sprint progress",
                topK=5,
            )
        )

        # Deterministic “foundational” outputs (placeholders) – kept structured and explainable.
        standup = StandupReport(
            teamName=None,
            items=[],
            highlights=[
                "Standup automation is enabled; awaiting team status inputs.",
            ],
        )

        blockers: list[Blocker] = []
        risks: list[RiskEscalation] = []
        nudges: list[IdleNudge] = []

        # Minimal heuristic: if memory is empty, reduce confidence and suggest collection.
        signals_used = [
            f"memory_hits={len(mem.hits)}",
            "workflow_step=" + stepSpec.stepId,
        ]
        assumptions = [
            "Memory hits represent the most recent team updates.",
            "Slack context is provided via tools when available.",
        ]

        recommendations: list[str] = []
        slack_actions: list[SlackAction] = []

        if len(mem.hits) == 0:
            recommendations.append("Collect team status via Slack prompt in the standup channel.")
            slack_actions.append(
                SlackAction(
                    actionType="post_message",
                    target=SlackTarget(channelId=None, userId=None),
                    text="Standup time: please share yesterday/today/blockers in this thread.",
                    metadata={"reason": "status_collection"},
                )
            )
            confidence = Confidence(
                score=0.35,
                rationale="Low confidence: no recent memory hits available to infer status/blockers.",
                signals={"memory_hits": 0},
            )
        else:
            recommendations.append("Summarize recent updates and highlight blockers for quick resolution.")
            confidence = Confidence(
                score=0.7,
                rationale="Moderate confidence: memory hits available but Slack/tool context not yet fetched.",
                signals={"memory_hits": len(mem.hits)},
            )

        explainability = Explainability(
            recommendations=recommendations,
            rationale="Recommendations were generated from available memory signals and workflow context.",
            signalsUsed=signals_used,
            assumptions=assumptions,
            references=[h.itemId for h in mem.hits],
        )

        output = ScrumMasterOutput(
            standup=standup,
            blockers=blockers,
            idleNudges=nudges,
            sprintSummary=SprintSummary(
                periodLabel="current_sprint",
                summary="Sprint summary placeholder: integrate workflow persistence and team updates.",
                keyWins=[],
                openRisks=[],
                nextFocus=["Collect status", "Surface blockers", "Escalate risks as needed"],
            ),
            risks=risks,
            explainability=explainability,
            confidence=confidence,
            slackActions=slack_actions,
        )

        await self._emit(
            context=context,
            stepId=stepSpec.stepId,
            eventType=AgentEventType.AGENT_RUN_COMPLETED,
            payload={"role": self.roleName, "confidence": output.confidence.score},
        )

        return AgentOutputEnvelope(
            agentRole="scrum_master",
            output=output.model_dump(),
            explainability=output.explainability.model_dump(),
            confidence={
                "score": output.confidence.score,
                "rationale": output.confidence.rationale,
                "signals": output.confidence.signals,
            },
        )

    async def _emit(self, *, context: AgentRunContext, stepId: str, eventType: AgentEventType, payload: dict[str, Any]) -> None:
        if self._eventEmitter is None:
            return
        evt = AgentEventEnvelope(
            eventType=eventType,
            tenantId=context.tenantId,
            jobId=context.jobId,
            workflowKey=context.workflowKey,
            workflowVersion=context.workflowVersion,
            workspaceId=context.workspaceId,
            agentRole="scrum_master",
            stepId=stepId,
            requestId=context.requestId,
            traceId=context.traceId,
            payload=payload,
        )
        # eventEmitter is intentionally untyped here; must implement `.emit(event)` coroutine.
        await self._eventEmitter.emit(evt)

