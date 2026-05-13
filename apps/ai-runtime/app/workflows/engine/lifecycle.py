from __future__ import annotations

from dataclasses import dataclass

from ..state.types import WorkflowRunStatus, WorkflowStepBoundary


@dataclass(frozen=True)
class WorkflowStepBoundaryPolicy:
    """
    Defines deterministic checkpoint boundaries used by LangGraph nodes.

    The workflow runner will ask the graph factory (or configuration) which boundary
    applies at each node/transition.
    """

    # Example: list of stable stepIds that must checkpoint.
    checkpointedBoundaries: tuple[WorkflowStepBoundary, ...]


@dataclass(frozen=True)
class WorkflowLifecycleOutcome:
    """
    Result of running the workflow engine for a command.

    Business logic should interpret these outcomes; engine just produces them.
    """

    status: WorkflowRunStatus
    checkpointSeq: int | None = None
    checkpointId: str | None = None

