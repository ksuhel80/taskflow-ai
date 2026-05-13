from __future__ import annotations

from ..prompt_manager import PromptTemplate


def researcher_prompt_template(*, templateVersion: str = "1") -> PromptTemplate:
    return PromptTemplate(
        name="researcher.system",
        systemTemplate="You are the Researcher agent. Analyze sprint history and produce key findings.",
        userTemplate="Sprint context:\n{{sprintContext}}\n\nProvide a structured research output.",
        templateVersion=templateVersion,
    )

