from __future__ import annotations

import datetime as dt
import uuid
from typing import Any, Callable

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.config import get_stream_writer
from langgraph.graph import END, START, StateGraph
from langgraph.types import RetryPolicy
from langgraph.types import Command, interrupt

from .events import commit_event_payload, sprint_event_payload
from .ports import (
    AuditLoggerPort,
    ConfidenceScorerPort,
    ExplainabilityPort,
    LLMUsageRecorderPort,
    PlannerPort,
    ResearcherPort,
    ReviewerPort,
    SprintContextCollectorPort,
    SprintCommitPort,
)
from .state import (
    ConfidenceOutput,
    Explainability,
    HumanApproval,
    LLMUsage,
    PlannerOutput,
    ResearcherOutput,
    ReviewerOutput,
    SprintCommitPayload,
    SprintContext,
    SprintPlanningState,
    WorkflowError,
)


class TransientWorkflowError(Exception):
    """Raised by nodes when errors are retryable (e.g., provider timeouts)."""


class NonRetryableWorkflowError(Exception):
    """Raised by nodes when errors are non-retryable (e.g., invalid deterministic inputs)."""


def _now_iso() -> str:
    return dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc).isoformat()


class _NoopAuditLogger(AuditLoggerPort):
    async def log_audit_event(
        self, *, tenantId: str, jobId: str, workflowKey: str, workflowVersion: str, eventType: str, payload: dict[str, Any] | None
    ) -> None:
        return


class _NoopExplainability(ExplainabilityPort):
    async def build_explainability(self, *, agent: str, rationale: str, assumptions: list[str]) -> dict[str, Any]:
        return {"agent": agent, "rationale": rationale, "assumptions": assumptions}


class _NoopCostRecorder(LLMUsageRecorderPort):
    async def record_llm_usage(self, *, usage: LLMUsage, eventType: str, metadata: dict[str, Any] | None = None) -> None:
        return


class _NoopCommitter(SprintCommitPort):
    async def commit_sprint(self, *, tenantId: str, jobId: str, commit: dict[str, Any]) -> None:
        return


class _NoopContextCollector(SprintContextCollectorPort):
    async def collect_context(self, *, inputPayload: dict[str, Any]) -> dict[str, Any]:
        # Placeholder: in production, pull sprint context from backlog/history sources.
        return {"sprintGoal": str(inputPayload.get("sprintGoal", "unknown")), "historyRef": None, "backlogRef": None}


class _NoopResearcher(ResearcherPort):
    async def analyze_history(self, *, context: dict[str, Any], historyRef: str | None) -> ResearcherOutput:
        return {
            "summary": "research placeholder",
            "keyFindings": [],
            "risksAndDependencies": [],
            "explainability": {"agent": "researcher", "rationale": "placeholder", "assumptions": []},
            "llmUsage": None,
        }


class _NoopPlanner(PlannerPort):
    async def propose_allocation(self, *, context: dict[str, Any], researcher: ResearcherOutput) -> PlannerOutput:
        return {
            "allocation": {},
            "capacityAssumptions": {},
            "explainability": {"agent": "planner", "rationale": "placeholder", "assumptions": []},
            "llmUsage": None,
        }


class _NoopReviewer(ReviewerPort):
    async def validate_workload(self, *, context: dict[str, Any], planner: PlannerOutput) -> ReviewerOutput:
        return {
            "workloadBalanceOk": True,
            "issues": [],
            "recommendations": [],
            "explainability": {"agent": "reviewer", "rationale": "placeholder", "assumptions": []},
            "llmUsage": None,
        }


class _NoopConfidenceScorer(ConfidenceScorerPort):
    async def score_confidence(self, *, context: dict[str, Any], outputs: dict[str, Any]) -> ConfidenceOutput:
        return {"score": 0.5, "rationale": "placeholder", "llmUsage": None}


def build_sprint_planning_graph(
    *,
    checkpointer: Any | None = None,
    contextCollector: SprintContextCollectorPort | None = None,
    researcher: ResearcherPort | None = None,
    planner: PlannerPort | None = None,
    reviewer: ReviewerPort | None = None,
    confidenceScorer: ConfidenceScorerPort | None = None,
    auditLogger: AuditLoggerPort | None = None,
    explainabilityBuilder: ExplainabilityPort | None = None,
    costRecorder: LLMUsageRecorderPort | None = None,
    committer: SprintCommitPort | None = None,
) -> Any:
    """
    Build and compile the Sprint Planning LangGraph workflow.

    This function is dependency-injected with ports so the runtime can connect to:
    - LiteLLM gateway
    - memory retrieval
    - audit persistence
    - workflow persistence / checkpoints
    - DB commiters
    """

    # Default to an in-memory checkpointer so interrupts work in dev/test.
    # Production should inject a persistent checkpointer (e.g., PostgresSaver).
    checkpointer = checkpointer or InMemorySaver()

    contextCollector = contextCollector or _NoopContextCollector()
    researcher = researcher or _NoopResearcher()
    planner = planner or _NoopPlanner()
    reviewer = reviewer or _NoopReviewer()
    confidenceScorer = confidenceScorer or _NoopConfidenceScorer()
    auditLogger = auditLogger or _NoopAuditLogger()
    explainabilityBuilder = explainabilityBuilder or _NoopExplainability()
    costRecorder = costRecorder or _NoopCostRecorder()
    committer = committer or _NoopCommitter()

    # ----------------------
    # Nodes (typed state)
    # ----------------------

    async def check_cancelled(state: SprintPlanningState) -> dict[str, Any]:
        writer = get_stream_writer()
        if state.get("cancelRequested"):
            await auditLogger.log_audit_event(
                tenantId=state["tenantId"],
                jobId=state["jobId"],
                workflowKey=state["workflowKey"],
                workflowVersion=state["workflowVersion"],
                eventType="workflow_cancelled",
                payload={"reason": state.get("cancelReason")},
            )
            writer(
                sprint_event_payload(
                    eventType="workflow_cancelled",
                    tenantId=state["tenantId"],
                    jobId=state["jobId"],
                    workflowKey=state["workflowKey"],
                    workflowVersion=state["workflowVersion"],
                    reason=state.get("cancelReason"),
                )
            )
            return {"status": "CANCELLED"}
        return {}

    async def collect_sprint_context(state: SprintPlanningState) -> dict[str, Any]:
        writer = get_stream_writer()
        writer(
            sprint_event_payload(
                eventType="step_started",
                tenantId=state["tenantId"],
                jobId=state["jobId"],
                workflowKey=state["workflowKey"],
                workflowVersion=state["workflowVersion"],
                step="collect_sprint_context",
                stepSeq=state.get("stepSeq", 0) + 1,
            )
        )

        try:
            ctx = await contextCollector.collect_context(inputPayload=state.get("context", {}))
            explain = await explainabilityBuilder.build_explainability(
                agent="context_collector",
                rationale="Collected sprint context from provided references (placeholder).",
                assumptions=["inputPayload contains required refs"],
            )
            await auditLogger.log_audit_event(
                tenantId=state["tenantId"],
                jobId=state["jobId"],
                workflowKey=state["workflowKey"],
                workflowVersion=state["workflowVersion"],
                eventType="audit_context_collected",
                payload={"sprintGoal": ctx.get("sprintGoal")},
            )
            return {
                "context": ctx,
                "explainabilityLog": state.get("explainabilityLog", []) + [explain],  # type: ignore[operator]
                "status": "RUNNING",
            }
        except TransientWorkflowError:
            raise
        except Exception as exc:
            return _set_error_and_emit(state, step="collect_sprint_context", exc=exc)

    async def researcher_analyze_history(state: SprintPlanningState) -> dict[str, Any]:
        writer = get_stream_writer()
        try:
            writer(
                sprint_event_payload(
                    eventType="step_started",
                    tenantId=state["tenantId"],
                    jobId=state["jobId"],
                    workflowKey=state["workflowKey"],
                    workflowVersion=state["workflowVersion"],
                    step="researcher_analyze_history",
                    stepSeq=state.get("stepSeq", 0) + 1,
                )
            )

            out = await researcher.analyze_history(context=state["context"], historyRef=state["context"].get("historyRef"))
            if out.get("llmUsage"):
                await costRecorder.record_llm_usage(usage=out["llmUsage"], eventType="researcher_llm_usage", metadata=None)

            await auditLogger.log_audit_event(
                tenantId=state["tenantId"],
                jobId=state["jobId"],
                workflowKey=state["workflowKey"],
                workflowVersion=state["workflowVersion"],
                eventType="audit_researcher_completed",
                payload={"summary": out.get("summary")},
            )

            return {
                "researcher": out,
                "explainabilityLog": state.get("explainabilityLog", []) + [out.get("explainability")],  # type: ignore[list-item]
            }
        except TransientWorkflowError:
            raise
        except Exception as exc:
            return _set_error_and_emit(state, step="researcher_analyze_history", exc=exc)

    async def planner_propose_allocation(state: SprintPlanningState) -> dict[str, Any]:
        writer = get_stream_writer()
        try:
            writer(
                sprint_event_payload(
                    eventType="step_started",
                    tenantId=state["tenantId"],
                    jobId=state["jobId"],
                    workflowKey=state["workflowKey"],
                    workflowVersion=state["workflowVersion"],
                    step="planner_propose_allocation",
                    stepSeq=state.get("stepSeq", 0) + 1,
                )
            )

            out = await planner.propose_allocation(context=state["context"], researcher=state["researcher"])
            if out.get("llmUsage"):
                await costRecorder.record_llm_usage(usage=out["llmUsage"], eventType="planner_llm_usage", metadata=None)

            return {
                "planner": out,
                "explainabilityLog": state.get("explainabilityLog", []) + [out.get("explainability")],  # type: ignore[list-item]
            }
        except Exception as exc:
            return _set_error_and_emit(state, step="planner_propose_allocation", exc=exc)

    async def reviewer_validate_workload(state: SprintPlanningState) -> dict[str, Any]:
        writer = get_stream_writer()
        try:
            writer(
                sprint_event_payload(
                    eventType="step_started",
                    tenantId=state["tenantId"],
                    jobId=state["jobId"],
                    workflowKey=state["workflowKey"],
                    workflowVersion=state["workflowVersion"],
                    step="reviewer_validate_workload",
                    stepSeq=state.get("stepSeq", 0) + 1,
                )
            )

            out = await reviewer.validate_workload(context=state["context"], planner=state["planner"])
            if out.get("llmUsage"):
                await costRecorder.record_llm_usage(usage=out["llmUsage"], eventType="reviewer_llm_usage", metadata=None)

            return {
                "reviewer": out,
                "explainabilityLog": state.get("explainabilityLog", []) + [out.get("explainability")],  # type: ignore[list-item]
            }
        except Exception as exc:
            return _set_error_and_emit(state, step="reviewer_validate_workload", exc=exc)

    async def generate_confidence_score(state: SprintPlanningState) -> dict[str, Any]:
        writer = get_stream_writer()
        try:
            out = await confidenceScorer.score_confidence(
                context=state["context"],
                outputs={"researcher": state.get("researcher"), "planner": state.get("planner"), "reviewer": state.get("reviewer")},
            )
            if out.get("llmUsage"):
                await costRecorder.record_llm_usage(usage=out["llmUsage"], eventType="confidence_llm_usage", metadata=None)

            return {"confidence": out}
        except Exception as exc:
            return _set_error_and_emit(state, step="generate_confidence_score", exc=exc)

    async def human_approval_checkpoint(state: SprintPlanningState) -> dict[str, Any]:
        """
        Uses LangGraph interrupt() to pause for human approval.

        On resume, `approvalDecision` is the resume value returned from interrupt().
        """
        writer = get_stream_writer()

        # If already decided (e.g. replay), allow passing through.
        approval = state.get("approval")
        if approval and approval.get("status") in ("APPROVED", "REJECTED"):
            return {}

        approvalId = approval.get("approvalId") if approval else None
        if not approvalId:
            approvalId = str(uuid.uuid4())

        approval_request: dict[str, Any] = {
            "approvalId": approvalId,
            "stepId": "human_approval_checkpoint",
            "summary": "Approve the proposed sprint allocation and confidence score?",
            "confidenceScore": state.get("confidence", {}).get("score"),
            "allocationPreview": state.get("planner", {}).get("allocation"),
        }

        writer(
            sprint_event_payload(
                eventType="approval_requested",
                tenantId=state["tenantId"],
                jobId=state["jobId"],
                workflowKey=state["workflowKey"],
                workflowVersion=state["workflowVersion"],
                approvalId=approvalId,
                step="human_approval_checkpoint",
            )
        )

        await auditLogger.log_audit_event(
            tenantId=state["tenantId"],
            jobId=state["jobId"],
            workflowKey=state["workflowKey"],
            workflowVersion=state["workflowVersion"],
            eventType="audit_approval_requested",
            payload={"approvalId": approvalId},
        )

        # Pause execution until human resumes with a decision value.
        # Resume value should be: {"decision":"APPROVED"|"REJECTED","decidedBy":"...","decisionReason":"..."}
        decision = interrupt(approval_request)

        writer(
            sprint_event_payload(
                eventType="approval_decided",
                tenantId=state["tenantId"],
                jobId=state["jobId"],
                workflowKey=state["workflowKey"],
                workflowVersion=state["workflowVersion"],
                approvalId=approvalId,
                decision=decision,
            )
        )

        # Normalize decision.
        dec = decision.get("decision") if isinstance(decision, dict) else None
        decidedBy = decision.get("decidedBy") if isinstance(decision, dict) else None
        reason = decision.get("decisionReason") if isinstance(decision, dict) else None
        decidedAt = _now_iso()

        status = "APPROVED" if dec == "APPROVED" else "REJECTED"
        return {
            "approval": {
                "approvalId": approvalId,
                "stepId": "human_approval_checkpoint",
                "requestedAtIso": _now_iso(),
                "summary": approval_request.get("summary", ""),
                "status": status,
                "decision": dec,
                "decidedAtIso": decidedAt,
                "decidedBy": decidedBy,
                "decisionReason": reason,
            },
        }

    async def commit_sprint_to_database(state: SprintPlanningState) -> dict[str, Any]:
        writer = get_stream_writer()
        try:
            writer(
                sprint_event_payload(
                    eventType="step_started",
                    tenantId=state["tenantId"],
                    jobId=state["jobId"],
                    workflowKey=state["workflowKey"],
                    workflowVersion=state["workflowVersion"],
                    step="commit_sprint_to_database",
                    stepSeq=state.get("stepSeq", 0) + 1,
                )
            )

            commit: SprintCommitPayload = {
                "sprintId": str(uuid.uuid4()),
                "allocation": state.get("planner", {}).get("allocation", {}),
                "confidenceScore": state.get("confidence", {}).get("score", 0.0),
                "artifacts": {
                    "researchSummary": state.get("researcher", {}).get("summary"),
                    "reviewIssues": state.get("reviewer", {}).get("issues"),
                },
            }

            await committer.commit_sprint(tenantId=state["tenantId"], jobId=state["jobId"], commit=commit)

            await auditLogger.log_audit_event(
                tenantId=state["tenantId"],
                jobId=state["jobId"],
                workflowKey=state["workflowKey"],
                workflowVersion=state["workflowVersion"],
                eventType="audit_sprint_committed",
                payload={"sprintId": commit.get("sprintId")},
            )

            writer(commit_event_payload(commit=commit))
            return {
                "commit": commit,
                "status": "COMPLETED",
            }
        except Exception as exc:
            return _set_error_and_emit(state, step="commit_sprint_to_database", exc=exc)

    async def human_approval_rejected(state: SprintPlanningState) -> dict[str, Any]:
        writer = get_stream_writer()
        err: WorkflowError = {
            "errorCode": "APPROVAL_REJECTED",
            "errorCategory": "WORKFLOW_EXECUTION",
            "message": "Human rejected sprint allocation.",
            "details": {"approvalId": state.get("approval", {}).get("approvalId")},
        }
        await auditLogger.log_audit_event(
            tenantId=state["tenantId"],
            jobId=state["jobId"],
            workflowKey=state["workflowKey"],
            workflowVersion=state["workflowVersion"],
            eventType="audit_approval_rejected",
            payload={"approvalId": state.get("approval", {}).get("approvalId")},
        )
        writer(
            sprint_event_payload(
                eventType="workflow_failed",
                tenantId=state["tenantId"],
                jobId=state["jobId"],
                workflowKey=state["workflowKey"],
                workflowVersion=state["workflowVersion"],
                errorCode=err["errorCode"],
            )
        )
        return {"status": "FAILED", "error": err}

    async def handle_error(state: SprintPlanningState) -> dict[str, Any]:
        writer = get_stream_writer()
        err = state.get("error")
        await auditLogger.log_audit_event(
            tenantId=state["tenantId"],
            jobId=state["jobId"],
            workflowKey=state["workflowKey"],
            workflowVersion=state["workflowVersion"],
            eventType="workflow_failed",
            payload=err,
        )
        writer(
            sprint_event_payload(
                eventType="workflow_failed",
                tenantId=state["tenantId"],
                jobId=state["jobId"],
                workflowKey=state["workflowKey"],
                workflowVersion=state["workflowVersion"],
                errorCode=(err or {}).get("errorCode"),
                retryable=False,
            )
        )
        return {"status": "FAILED"}

    async def cancelled_end(state: SprintPlanningState) -> dict[str, Any]:
        # Cancellation path terminates the workflow without marking it as a failure.
        return {"status": "CANCELLED"}

    # Helper to set error and emit.
    def _set_error_and_emit(state: SprintPlanningState, *, step: str, exc: Exception) -> dict[str, Any]:
        writer = get_stream_writer()

        err: WorkflowError = {
            "errorCode": exc.__class__.__name__,
            "errorCategory": "WORKFLOW_EXECUTION",
            "message": str(exc),
            "details": {"step": step},
        }
        writer(
            sprint_event_payload(
                eventType="step_failed",
                tenantId=state["tenantId"],
                jobId=state["jobId"],
                workflowKey=state["workflowKey"],
                workflowVersion=state["workflowVersion"],
                step=step,
                errorCode=err["errorCode"],
            )
        )
        return {"status": "FAILED", "error": err}

    # ----------------------
    # Graph definition (nodes/edges)
    # ----------------------

    graph_builder = StateGraph(SprintPlanningState)

    # Cancellation gating at top
    graph_builder.add_node("check_cancelled", check_cancelled)

    # Steps
    graph_builder.add_node("collect_sprint_context", collect_sprint_context)
    graph_builder.add_node("researcher_analyze_history", researcher_analyze_history, retry_policy=RetryPolicy(max_attempts=3))
    graph_builder.add_node("planner_propose_allocation", planner_propose_allocation, retry_policy=RetryPolicy(max_attempts=3))
    graph_builder.add_node("reviewer_validate_workload", reviewer_validate_workload, retry_policy=RetryPolicy(max_attempts=3))
    graph_builder.add_node("generate_confidence_score", generate_confidence_score, retry_policy=RetryPolicy(max_attempts=3))
    graph_builder.add_node("human_approval_checkpoint", human_approval_checkpoint)
    graph_builder.add_node("commit_sprint_to_database", commit_sprint_to_database)
    graph_builder.add_node("human_approval_rejected", human_approval_rejected)
    graph_builder.add_node("handle_error", handle_error)
    graph_builder.add_node("cancelled_end", cancelled_end)

    # Route after check_cancelled
    def route_after_cancel(state: SprintPlanningState) -> str:
        if state.get("status") == "CANCELLED":
            return "cancelled_end"
        return "collect_sprint_context"

    graph_builder.add_conditional_edges("check_cancelled", route_after_cancel)

    # After each AI step, route based on whether state.error exists.
    graph_builder.add_edge(START, "check_cancelled")

    # Fixed edges with conditional routing where appropriate.
    def route_after_collect(state: SprintPlanningState) -> str:
        if state.get("status") == "FAILED" or state.get("error") is not None:
            return "handle_error"
        return "researcher_analyze_history"

    def route_after_researcher(state: SprintPlanningState) -> str:
        if state.get("status") == "FAILED" or state.get("error") is not None:
            return "handle_error"
        return "planner_propose_allocation"

    def route_after_planner(state: SprintPlanningState) -> str:
        if state.get("status") == "FAILED" or state.get("error") is not None:
            return "handle_error"
        return "reviewer_validate_workload"

    def route_after_reviewer(state: SprintPlanningState) -> str:
        if state.get("status") == "FAILED" or state.get("error") is not None:
            return "handle_error"
        return "generate_confidence_score"

    def route_after_confidence(state: SprintPlanningState) -> str:
        if state.get("status") == "FAILED" or state.get("error") is not None:
            return "handle_error"
        return "human_approval_checkpoint"

    graph_builder.add_conditional_edges("collect_sprint_context", route_after_collect)
    graph_builder.add_conditional_edges("researcher_analyze_history", route_after_researcher)
    graph_builder.add_conditional_edges("planner_propose_allocation", route_after_planner)
    graph_builder.add_conditional_edges("reviewer_validate_workload", route_after_reviewer)
    graph_builder.add_conditional_edges("generate_confidence_score", route_after_confidence)

    # Conditional after approval
    def route_after_approval(state: SprintPlanningState) -> str:
        if state.get("status") == "FAILED" or state.get("error") is not None:
            return "handle_error"
        approval = state.get("approval") or {}
        if approval.get("status") == "APPROVED":
            return "commit_sprint_to_database"
        if approval.get("status") == "REJECTED":
            return "human_approval_rejected"
        # If missing (shouldn't happen), fail-safe.
        return "human_approval_rejected"

    graph_builder.add_conditional_edges("human_approval_checkpoint", route_after_approval)

    # Commit can fail; terminate accordingly.
    def route_after_commit(state: SprintPlanningState) -> str:
        if state.get("status") == "FAILED" or state.get("error") is not None:
            return "handle_error"
        return END

    graph_builder.add_conditional_edges("commit_sprint_to_database", route_after_commit)
    graph_builder.add_edge("human_approval_rejected", END)
    graph_builder.add_edge("handle_error", END)
    graph_builder.add_edge("cancelled_end", END)

    # Compile with checkpointer for stateful execution and interrupts persistence.
    graph = graph_builder.compile(checkpointer=checkpointer)
    return graph

