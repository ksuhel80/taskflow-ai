from __future__ import annotations

from typing import Any

from .state import SprintCommitPayload


def sprint_event_payload(*, eventType: str, tenantId: str, jobId: str, workflowKey: str, workflowVersion: str, **extra: Any) -> dict[str, Any]:
    """
    Creates a standardized custom event payload to be emitted via LangGraph streaming.
    """

    return {
        "eventType": eventType,
        "tenantId": tenantId,
        "jobId": jobId,
        "workflowKey": workflowKey,
        "workflowVersion": workflowVersion,
        **extra,
    }


def commit_event_payload(*, commit: SprintCommitPayload) -> dict[str, Any]:
    return {"commit": commit}

