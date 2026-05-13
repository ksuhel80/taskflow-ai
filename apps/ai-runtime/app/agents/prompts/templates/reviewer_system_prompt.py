from __future__ import annotations

from ..prompt_manager import PromptTemplate


def reviewer_prompt_template(*, templateVersion: str = "1") -> PromptTemplate:
    return PromptTemplate(
        name="reviewer.system",
        systemTemplate="You are the Reviewer agent. Validate workload balance and constraints.",
        userTemplate="Context:\n{{sprintContext}}\n\nPlanner allocation:\n{{plannerOutput}}\n\nValidate workload balance and provide recommendations.",
        templateVersion=templateVersion,
    )

