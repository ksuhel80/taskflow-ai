from __future__ import annotations

from typing import Any, Protocol

from .state import LLMUsage, ResearcherOutput, PlannerOutput, ReviewerOutput, ConfidenceOutput


class SprintContextCollectorPort(Protocol):
    async def collect_context(self, *, inputPayload: dict[str, Any]) -> dict[str, Any]: ...


class ResearcherPort(Protocol):
    async def analyze_history(self, *, context: dict[str, Any], historyRef: str | None) -> ResearcherOutput: ...


class PlannerPort(Protocol):
    async def propose_allocation(self, *, context: dict[str, Any], researcher: ResearcherOutput) -> PlannerOutput: ...


class ReviewerPort(Protocol):
    async def validate_workload(
        self, *, context: dict[str, Any], planner: PlannerOutput
    ) -> ReviewerOutput: ...


class ConfidenceScorerPort(Protocol):
    async def score_confidence(self, *, context: dict[str, Any], outputs: dict[str, Any]) -> ConfidenceOutput: ...


class AuditLoggerPort(Protocol):
    async def log_audit_event(
        self,
        *,
        tenantId: str,
        jobId: str,
        workflowKey: str,
        workflowVersion: str,
        eventType: str,
        payload: dict[str, Any] | None,
    ) -> None: ...


class ExplainabilityPort(Protocol):
    async def build_explainability(self, *, agent: str, rationale: str, assumptions: list[str]) -> dict[str, Any]: ...


class LLMUsageRecorderPort(Protocol):
    async def record_llm_usage(self, *, usage: LLMUsage, eventType: str, metadata: dict[str, Any] | None = None) -> None: ...


class SprintCommitPort(Protocol):
    async def commit_sprint(
        self,
        *,
        tenantId: str,
        jobId: str,
        commit: dict[str, Any],
    ) -> None: ...

