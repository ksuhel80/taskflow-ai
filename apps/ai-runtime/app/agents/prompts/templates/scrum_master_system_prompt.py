from __future__ import annotations

from ..prompt_manager import PromptTemplate


def scrum_master_prompt_template(*, templateVersion: str = "1") -> PromptTemplate:
    return PromptTemplate(
        name="scrum_master.system",
        systemTemplate=(
            "You are the Scrum Master Agent for TaskFlow AI.\n"
            "You produce structured, actionable, explainable recommendations for:\n"
            "- autonomous standups\n"
            "- blocker detection\n"
            "- idle task nudging\n"
            "- sprint summaries\n"
            "- team status collection\n"
            "- risk escalation\n\n"
            "Rules:\n"
            "- Output MUST be valid JSON matching the ScrumMasterOutput schema.\n"
            "- Do not include secrets or sensitive personal data.\n"
            "- Prefer citations as references to internal IDs/links, not raw text dumps.\n"
            "- When confidence is low, explain why and propose safe next steps.\n"
        ),
        userTemplate=(
            "Workspace:\n{{workspace}}\n\n"
            "Workflow context (redacted-safe):\n{{workflowContext}}\n\n"
            "Memory hits (redacted-safe):\n{{memoryHits}}\n\n"
            "Slack context (optional, redacted-safe):\n{{slackContext}}\n\n"
            "Return ScrumMasterOutput JSON.\n"
        ),
        templateVersion=templateVersion,
    )

