from __future__ import annotations

from typing import Any, Protocol


class LangGraphGraphFactory(Protocol):
    """
    Factory that returns a LangGraph graph instance.

    Concrete implementations live in `graphs/definitions/*` and must encapsulate
    LangGraph wiring and step/node declarations.
    """

    def build(self, *, workflowKey: str, workflowVersion: str, workflowInput: dict[str, Any]) -> Any: ...


def build_placeholder_graph(*, workflowKey: str, workflowVersion: str, workflowInput: dict[str, Any]) -> Any:
    """
    Placeholder builder. Replace with real LangGraph graph construction later.
    """

    raise NotImplementedError("Graph construction is not implemented yet")

