from __future__ import annotations

from typing import Any, Protocol

from ..state.types import ApprovalDecision, ApprovalRequest


class ApprovalDecisionPort(Protocol):
    """
    Contract for submitting human approval decisions.
    Implementations typically validate authorization and call persistence.
    """

    def decide(self, *, decision: ApprovalDecision, tenantId: str, jobId: str) -> None: ...


class ApprovalPort(Protocol):
    """
    Contract for pausing/resuming workflows around human approvals.
    """

    def request_approval(self, *, approval: ApprovalRequest, tenantId: str, jobId: str) -> None: ...

    def get_pending_approval(self, *, tenantId: str, jobId: str, approvalId: str) -> ApprovalRequest: ...

    def resume_after_approval(
        self, *, tenantId: str, jobId: str, approvalId: str, decisionPayload: dict[str, Any]
    ) -> None: ...

