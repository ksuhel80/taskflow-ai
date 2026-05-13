from __future__ import annotations


class PostHogProvider:
    """
    PostHog analytics adapter scaffold.

    Intended for product analytics and operational usage signals:
    - workflow initiated/completed
    - approval requested/decided
    - user-visible failures
    """

    def track(self, *, event: str, distinct_id: str, properties: dict[str, object]) -> None:
        # Placeholder; integrate posthog-python client in runtime.
        return

