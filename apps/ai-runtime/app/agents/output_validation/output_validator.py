from __future__ import annotations

from typing import Any, Protocol

from pydantic import BaseModel

from ..base.contracts import AgentError, AgentRole, AgentRunContext


class OutputValidationError(Exception):
    pass


class OutputValidatorPort(Protocol):
    async def validate(
        self,
        *,
        context: AgentRunContext,
        agentRole: AgentRole,
        output: dict[str, Any],
    ) -> BaseModel: ...


class PydanticOutputValidator(OutputValidatorPort):
    """
    Validates LLM/agent output against role-specific Pydantic models.

    This is design-only: model registry must be wired later.
    """

    def __init__(self, *, modelByRole: dict[AgentRole, type[BaseModel]]) -> None:
        self._modelByRole = modelByRole

    async def validate(
        self,
        *,
        context: AgentRunContext,
        agentRole: AgentRole,
        output: dict[str, Any],
    ) -> BaseModel:
        if agentRole not in self._modelByRole:
            raise OutputValidationError(f"No output model registered for role: {agentRole}")
        model = self._modelByRole[agentRole]
        try:
            return model.model_validate(output)
        except Exception as exc:
            # The caller/engine can decide retry vs fail based on error classification later.
            raise OutputValidationError(str(exc)) from exc


def classify_output_validation_failure(*, exc: Exception) -> AgentError:
    return AgentError(
        code="OUTPUT_VALIDATION_FAILED",
        category="NON_RETRYABLE",
        message="Agent output did not match the required structured schema.",
        details={"reason": str(exc)},
        retryable=False,
    )

