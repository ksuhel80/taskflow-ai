from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .tool_contracts import ToolSpec


@dataclass(frozen=True)
class RegisteredTool:
    spec: ToolSpec
    # executor is intentionally not typed as it is implementation-specific.
    # For architecture-only we accept a placeholder callable.
    executor: Callable[..., Any]


class ToolRegistry:
    """
    Tool registry for schema-first tool calling.

    Only contracts are enforced here; actual tool execution wiring is done later.
    """

    def __init__(self) -> None:
        self._tools: dict[str, RegisteredTool] = {}

    def register(self, *, spec: ToolSpec, executor: Callable[..., Any]) -> None:
        self._tools[spec.name] = RegisteredTool(spec=spec, executor=executor)

    def get(self, *, toolName: str) -> RegisteredTool:
        if toolName not in self._tools:
            raise KeyError(f"Unknown tool: {toolName}")
        return self._tools[toolName]

    def list_tool_specs(self) -> list[ToolSpec]:
        return [rt.spec for rt in self._tools.values()]

