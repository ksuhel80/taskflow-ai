from __future__ import annotations

from typing import Protocol

from .types import WorkflowEvent


class WorkflowEventEmitterPort(Protocol):
    """
    Event emitter contract for streaming updates and audit hooks.

    Implementations may publish to:
    - Redis Streams topics
    - SSE broker
    - audit logging pipelines

    No business logic should exist here.
    """

    def emit(self, event: WorkflowEvent) -> None: ...

