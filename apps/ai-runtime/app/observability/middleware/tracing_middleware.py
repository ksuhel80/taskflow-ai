from __future__ import annotations

from typing import Callable
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from ..tracing import TraceManager
from ..types import TraceContext


class TracingMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for request trace context propagation.
    """

    def __init__(self, app, *, tracer: TraceManager) -> None:
        super().__init__(app)
        self._tracer = tracer

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("x-request-id", uuid4().hex)
        incoming_trace = request.headers.get("x-trace-id")

        context = TraceContext(
            traceId=incoming_trace or uuid4().hex,
            requestId=request_id,
            correlationId=request.url.path,
        )
        span = self._tracer.start_span(name=f"http:{request.method}:{request.url.path}", context=context)

        try:
            response = await call_next(request)
            response.headers["x-request-id"] = request_id
            response.headers["x-trace-id"] = span.traceId
            self._tracer.end_span(context=span, ok=True)
            return response
        except Exception:
            self._tracer.end_span(context=span, ok=False, error_code="HTTP_REQUEST_FAILED")
            raise

