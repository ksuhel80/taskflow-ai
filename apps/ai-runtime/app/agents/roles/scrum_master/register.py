from __future__ import annotations

from pydantic import BaseModel

from ...prompts.prompt_manager import PromptManager
from ...tools.tool_registry import ToolRegistry
from ...output_validation.output_validator import PydanticOutputValidator
from ...base.contracts import AgentRole
from ...prompts.templates.scrum_master_system_prompt import scrum_master_prompt_template
from .output_schemas import ScrumMasterOutput
from .tools import (
    slack_get_recent_messages_tool,
    slack_list_channel_members_tool,
    slack_open_dm_tool,
    slack_post_message_tool,
)


def register_scrum_master_agent_assets(
    *,
    promptManager: PromptManager,
    toolRegistry: ToolRegistry,
) -> None:
    """
    Registers prompt templates and tool specs for the Scrum Master agent.
    Executors are intentionally not registered here (adapter wiring happens elsewhere).
    """

    promptManager.register_template(template=scrum_master_prompt_template())

    # Register tool specs with placeholder executors.
    # Real executors should be injected in the runtime DI container.
    toolRegistry.register(spec=slack_post_message_tool(), executor=lambda **_: None)
    toolRegistry.register(spec=slack_open_dm_tool(), executor=lambda **_: None)
    toolRegistry.register(spec=slack_list_channel_members_tool(), executor=lambda **_: None)
    toolRegistry.register(spec=slack_get_recent_messages_tool(), executor=lambda **_: None)


def scrum_master_output_validator() -> PydanticOutputValidator:
    """
    Returns an OutputValidator preconfigured with the Scrum Master output schema.
    """

    return PydanticOutputValidator(
        modelByRole={
            "scrum_master": ScrumMasterOutput,  # type: ignore[dict-item]
        }
    )

