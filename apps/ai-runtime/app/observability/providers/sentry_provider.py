from __future__ import annotations

from ..types import LogEvent, Severity


class SentryProvider:
    """
    Sentry adapter scaffold.

    Integrate with `sentry_sdk` in runtime bootstrap:
    - init DSN and environment
    - capture exceptions + performance transactions
    - attach tenant/workspace breadcrumbs
    """

    def emit_log(self, event: LogEvent) -> None:
        # Placeholder behavior: translate high severity logs to Sentry events.
        # Business/runtime integration intentionally omitted.
        if event.severity in {Severity.ERROR, Severity.FATAL}:
            return

    def capture_exception(self, exc: Exception, *, context: dict[str, object] | None = None) -> None:
        # Placeholder; hook sentry_sdk.capture_exception in implementation.
        return

