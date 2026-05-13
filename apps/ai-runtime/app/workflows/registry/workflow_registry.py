from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from pydantic import BaseModel, ConfigDict

from ..graphs.definitions import (
    daily_standup,
    meeting_transcript_processing,
    risk_prediction,
    sprint_planning,
    task_prioritization,
)


class WorkflowInputContract(BaseModel):
    """
    Design-time contract describing expected workflow input fields.

    This is not validated yet; the runtime will use actual schemas later.
    """

    model_config = ConfigDict(extra="allow")

    fields: dict[str, Any] = {}


class WorkflowOutputContract(BaseModel):
    model_config = ConfigDict(extra="allow")

    fields: dict[str, Any] = {}


@dataclass(frozen=True)
class WorkflowDefinition:
    workflowKey: str
    workflowVersion: str
    displayName: str
    description: str
    inputContract: WorkflowInputContract
    outputContract: WorkflowOutputContract
    graphBuilder: Callable[..., Any]  # placeholder: returns LangGraph graph object later


class WorkflowRegistry:
    """
    Registry of known workflows.

    This prevents queue commands, persistence, and graph builders from drifting.
    """

    def __init__(self) -> None:
        # Design-only default version. When you add new versions, keep old versions for resume compatibility.
        v1 = "1"
        self._defs: dict[str, WorkflowDefinition] = {
            sprint_planning.WORKFLOW_KEY: WorkflowDefinition(
                workflowKey=sprint_planning.WORKFLOW_KEY,
                workflowVersion=v1,
                displayName="Sprint Planning",
                description="Plans sprint scope, tasks, and acceptance criteria.",
                inputContract=WorkflowInputContract(),
                outputContract=WorkflowOutputContract(),
                graphBuilder=sprint_planning.build_graph,
            ),
            daily_standup.WORKFLOW_KEY: WorkflowDefinition(
                workflowKey=daily_standup.WORKFLOW_KEY,
                workflowVersion=v1,
                displayName="Daily Standup",
                description="Summarizes standup status and highlights blockers.",
                inputContract=WorkflowInputContract(),
                outputContract=WorkflowOutputContract(),
                graphBuilder=daily_standup.build_graph,
            ),
            meeting_transcript_processing.WORKFLOW_KEY: WorkflowDefinition(
                workflowKey=meeting_transcript_processing.WORKFLOW_KEY,
                workflowVersion=v1,
                displayName="Meeting Transcript Processing",
                description="Extracts action items, decisions, and summaries from transcripts.",
                inputContract=WorkflowInputContract(),
                outputContract=WorkflowOutputContract(),
                graphBuilder=meeting_transcript_processing.build_graph,
            ),
            risk_prediction.WORKFLOW_KEY: WorkflowDefinition(
                workflowKey=risk_prediction.WORKFLOW_KEY,
                workflowVersion=v1,
                displayName="Risk Prediction",
                description="Predicts potential project risks and mitigation actions.",
                inputContract=WorkflowInputContract(),
                outputContract=WorkflowOutputContract(),
                graphBuilder=risk_prediction.build_graph,
            ),
            task_prioritization.WORKFLOW_KEY: WorkflowDefinition(
                workflowKey=task_prioritization.WORKFLOW_KEY,
                workflowVersion=v1,
                displayName="Task Prioritization",
                description="Ranks tasks based on impact, urgency, and dependencies.",
                inputContract=WorkflowInputContract(),
                outputContract=WorkflowOutputContract(),
                graphBuilder=task_prioritization.build_graph,
            ),
        }

    def get(self, *, workflowKey: str, workflowVersion: str | None = None) -> WorkflowDefinition:
        if workflowKey not in self._defs:
            raise KeyError(f"Unknown workflowKey: {workflowKey}")
        definition = self._defs[workflowKey]

        if workflowVersion is not None and workflowVersion != definition.workflowVersion:
            # For safety, a real implementation should support multiple versions concurrently.
            raise KeyError(
                f"Workflow version mismatch for {workflowKey}. Expected={definition.workflowVersion} Got={workflowVersion}"
            )
        return definition

