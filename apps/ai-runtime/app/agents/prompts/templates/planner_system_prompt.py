from __future__ import annotations

from ..prompt_manager import PromptTemplate


def planner_prompt_template(*, templateVersion: str = "1") -> PromptTemplate:
    return PromptTemplate(
        name="planner.system",
        systemTemplate="You are the Planner agent. Propose sprint allocation with balanced workload.",
        userTemplate="Context:\n{{sprintContext}}\n\nResearch summary:\n{{researcherOutput}}\n\nReturn a structured planning output.",
        templateVersion=templateVersion,
    )

