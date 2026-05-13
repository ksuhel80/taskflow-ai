from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PromptTemplate:
    """
    Immutable prompt template definitions.

    Use versioning for auditability:
    - systemTemplateVersion
    - userTemplateVersion
    """

    name: str
    systemTemplate: str
    userTemplate: str
    templateVersion: str


class PromptManager:
    """
    Prompt management with workspace isolation.

    Responsibilities (design-only):
    - render system/user prompts using workspace variables
    - prevent prompt variable leakage across tenants/jobs
    - provide deterministic rendering inputs for persistence and audit later
    """

    def __init__(self) -> None:
        self._templates: dict[str, PromptTemplate] = {}

    def register_template(self, *, template: PromptTemplate) -> None:
        self._templates[template.name] = template

    def get_template(self, *, templateName: str) -> PromptTemplate:
        if templateName not in self._templates:
            raise KeyError(f"Unknown prompt template: {templateName}")
        return self._templates[templateName]

    def render(
        self,
        *,
        templateName: str,
        variables: dict[str, Any],
    ) -> dict[str, str]:
        """
        Returns:
        - systemPrompt
        - userPrompt

        Implementation should enforce:
        - deterministic template rendering
        - redaction-safe variable interpolation
        """

        template = self.get_template(templateName=templateName)
        # Template rendering is intentionally omitted from this architecture-only scaffold.
        raise NotImplementedError("PromptManager.render is not implemented yet")

