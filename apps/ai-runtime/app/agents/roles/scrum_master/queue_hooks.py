from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ...base.contracts import AgentRunContext, AgentStepSpec
from .agent import ScrumMasterAgent


class ScrumMasterQueueCommand(BaseModel):
    """
    Queue command contract for executing the Scrum Master agent asynchronously.

    This is intentionally minimal; queue transport details live elsewhere.
    """

    model_config = ConfigDict(extra="forbid")

    tenantId: str
    jobId: str
    workflowKey: str
    workflowVersion: str
    workspaceId: str

    stepId: str = "scrum_master"
    input: dict[str, Any] = Field(default_factory=dict)


async def handle_scrum_master_command(
    *,
    cmd: ScrumMasterQueueCommand,
    agent: ScrumMasterAgent,
) -> dict[str, Any]:
    """
    Queue execution hook.

    The Redis Streams consumer should decode a ScrumMasterQueueCommand and call this handler.
    Streaming is provided via the Agent event emitter passed into the agent constructor.
    """

    context = AgentRunContext(
        tenantId=cmd.tenantId,
        jobId=cmd.jobId,
        workflowKey=cmd.workflowKey,
        workflowVersion=cmd.workflowVersion,
        workspaceId=cmd.workspaceId,
    )
    step = AgentStepSpec(stepId=cmd.stepId)
    result = await agent.run(stepSpec=step, context=context)
    return result.model_dump()

