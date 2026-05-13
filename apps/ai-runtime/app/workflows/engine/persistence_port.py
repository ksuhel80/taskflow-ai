from __future__ import annotations

from typing import Any, Protocol

from ..state.types import WorkflowCheckpoint, WorkflowRunStatus, WorkflowState


class WorkflowPersistencePort(Protocol):
    """
    Persistence contract for workflow runs and checkpoints.

    Implementations may use:
    - PostgreSQL (Prisma-managed schema via a service)
    - Redis checkpointing (development)
    - a hybrid approach

    This port must be deterministic and idempotent at step boundaries.
    """

    def create_or_load_workflow_run(
        self,
        *,
        tenantId: str,
        jobId: str,
        workflowKey: str,
        workflowVersion: str,
        inputRef: str | None,
        metadata: dict[str, Any] | None,
    ) -> None:
        """
        Create a workflow run record if it doesn't exist.
        Implementations should be safe for idempotent retries.
        """
        ...

    def load_checkpoint(
        self,
        *,
        tenantId: str,
        jobId: str,
        checkpointId: str,
    ) -> WorkflowCheckpoint:
        ...

    def save_checkpoint(
        self,
        *,
        checkpoint: WorkflowCheckpoint,
        # Some implementations require run status updates in the same transaction.
        expectedRunStatus: WorkflowRunStatus | None = None,
    ) -> str:
        """
        Persist a checkpoint and return checkpointId.
        Implementations should ensure checkpointSeq and stateHash are consistent.
        """
        ...

    def update_run_status(
        self,
        *,
        tenantId: str,
        jobId: str,
        status: WorkflowRunStatus,
        errorCode: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        ...

    def append_audit_log(
        self,
        *,
        tenantId: str,
        jobId: str,
        workflowKey: str,
        workflowVersion: str,
        eventType: str,
        payload: dict[str, Any] | None,
    ) -> None:
        """
        Optional: append audit log entries to a durable store (append-only).
        """
        ...

