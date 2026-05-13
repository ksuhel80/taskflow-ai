from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class SlackTarget(BaseModel):
    model_config = ConfigDict(extra="forbid")

    channelId: str | None = None
    userId: str | None = None


class SlackAction(BaseModel):
    """
    Contract for Slack integration hooks (tool calling).
    Execution is handled by tool adapters outside the agent.
    """

    model_config = ConfigDict(extra="forbid")

    actionType: Literal["post_message", "open_dm", "schedule_message"]
    target: SlackTarget
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class Blocker(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: str
    severity: Literal["low", "medium", "high", "critical"]
    ownerHint: str | None = None
    evidence: list[str] = Field(default_factory=list)
    recommendedNextActions: list[str] = Field(default_factory=list)


class IdleNudge(BaseModel):
    model_config = ConfigDict(extra="forbid")

    userHint: str
    reason: str
    suggestedMessage: str
    suggestedSlackAction: SlackAction | None = None


class RiskEscalation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    severity: Literal["low", "medium", "high", "critical"]
    rationale: str
    escalationSlackAction: SlackAction | None = None


class StandupItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    member: str
    yesterday: str | None = None
    today: str | None = None
    blockers: list[str] = Field(default_factory=list)


class StandupReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    createdAt: datetime = Field(default_factory=datetime.utcnow)
    teamName: str | None = None
    items: list[StandupItem] = Field(default_factory=list)
    highlights: list[str] = Field(default_factory=list)


class SprintSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    periodLabel: str
    summary: str
    keyWins: list[str] = Field(default_factory=list)
    openRisks: list[str] = Field(default_factory=list)
    nextFocus: list[str] = Field(default_factory=list)


class Explainability(BaseModel):
    model_config = ConfigDict(extra="forbid")

    recommendations: list[str] = Field(default_factory=list)
    rationale: str
    signalsUsed: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)


class Confidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    score: float = Field(ge=0.0, le=1.0)
    rationale: str
    signals: dict[str, Any] = Field(default_factory=dict)


class ScrumMasterOutput(BaseModel):
    """
    Structured output schema for Scrum Master Agent.
    """

    model_config = ConfigDict(extra="forbid")

    schemaVersion: str = "1"
    standup: StandupReport | None = None
    blockers: list[Blocker] = Field(default_factory=list)
    idleNudges: list[IdleNudge] = Field(default_factory=list)
    sprintSummary: SprintSummary | None = None
    risks: list[RiskEscalation] = Field(default_factory=list)

    explainability: Explainability
    confidence: Confidence
    slackActions: list[SlackAction] = Field(default_factory=list)

