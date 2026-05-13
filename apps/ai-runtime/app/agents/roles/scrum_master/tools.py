from __future__ import annotations

from ...tools.tool_contracts import ToolSpec


def slack_post_message_tool() -> ToolSpec:
    return ToolSpec(
        name="slack_post_message",
        description="Post a message to a Slack channel or DM (hook only).",
        inputSchema={
            "type": "object",
            "properties": {
                "channelId": {"type": ["string", "null"]},
                "userId": {"type": ["string", "null"]},
                "text": {"type": "string"},
                "metadata": {"type": "object"},
            },
            "required": ["text"],
            "additionalProperties": False,
        },
        outputSchema={
            "type": "object",
            "properties": {
                "ok": {"type": "boolean"},
                "messageTs": {"type": ["string", "null"]},
            },
            "required": ["ok"],
            "additionalProperties": False,
        },
    )


def slack_get_recent_messages_tool() -> ToolSpec:
    return ToolSpec(
        name="slack_get_recent_messages",
        description="Fetch recent Slack messages for a channel (hook only).",
        inputSchema={
            "type": "object",
            "properties": {
                "channelId": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 200},
            },
            "required": ["channelId"],
            "additionalProperties": False,
        },
        outputSchema={
            "type": "object",
            "properties": {
                "ok": {"type": "boolean"},
                "messages": {"type": "array", "items": {"type": "object"}},
            },
            "required": ["ok"],
            "additionalProperties": False,
        },
    )


def slack_list_channel_members_tool() -> ToolSpec:
    return ToolSpec(
        name="slack_list_channel_members",
        description="List Slack channel members (hook only).",
        inputSchema={
            "type": "object",
            "properties": {"channelId": {"type": "string"}},
            "required": ["channelId"],
            "additionalProperties": False,
        },
        outputSchema={
            "type": "object",
            "properties": {"ok": {"type": "boolean"}, "members": {"type": "array", "items": {"type": "string"}}},
            "required": ["ok"],
            "additionalProperties": False,
        },
    )


def slack_open_dm_tool() -> ToolSpec:
    return ToolSpec(
        name="slack_open_dm",
        description="Open a DM with a user (hook only).",
        inputSchema={
            "type": "object",
            "properties": {"userId": {"type": "string"}},
            "required": ["userId"],
            "additionalProperties": False,
        },
        outputSchema={
            "type": "object",
            "properties": {"ok": {"type": "boolean"}, "channelId": {"type": ["string", "null"]}},
            "required": ["ok"],
            "additionalProperties": False,
        },
    )

