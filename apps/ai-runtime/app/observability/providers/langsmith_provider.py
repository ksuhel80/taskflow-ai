from __future__ import annotations

from ..types import TraceContext


class LangSmithTracingProvider:
    """
    LangSmith tracing adapter scaffold.

    Intended usage:
    - create traces around workflow/agent execution boundaries
    - attach metadata for model/provider/cost/confidence
    - correlate with workflowRunId and agentRunId
    """

    def start_span(self, *, name: str, context: TraceContext | None = None) -> TraceContext:
        if context:
            return context
        # Placeholder IDs; real impl should use OpenTelemetry / LangSmith span ids.
        return TraceContext(traceId=f"ls-{name}", spanId="root")

    def end_span(self, *, context: TraceContext, ok: bool = True, error_code: str | None = None) -> None:
        return

