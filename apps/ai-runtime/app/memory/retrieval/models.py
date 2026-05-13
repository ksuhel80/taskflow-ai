from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class MemoryDomain(str, Enum):
    SEMANTIC = "SEMANTIC"
    DECISION = "DECISION"
    PREFERENCE = "PREFERENCE"


class RetrievalMode(str, Enum):
    VECTOR = "VECTOR"
    HYBRID = "HYBRID"


class MemoryMetadataFilter(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sourceType: str | None = None
    sourceId: str | None = None
    tagsAny: list[str] = Field(default_factory=list)
    tagsAll: list[str] = Field(default_factory=list)
    createdAfter: datetime | None = None
    createdBefore: datetime | None = None


class MemoryQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenantId: str
    workspaceId: str
    queryText: str

    domain: MemoryDomain | None = None
    namespaceType: str | None = None
    namespaceKey: str | None = None

    topK: int = 10
    mode: RetrievalMode = RetrievalMode.HYBRID
    minVectorScore: float | None = None
    metadataFilter: MemoryMetadataFilter | None = None

    # Context assembly budget (rough token budget)
    maxContextTokens: int = 2500


class MemoryRecord(BaseModel):
    """
    Canonical retrieval record from persistence layer.

    `embedding` may be omitted when not needed by a retrieval path.
    """

    model_config = ConfigDict(extra="forbid")

    memoryId: str
    tenantId: str
    workspaceId: str
    domain: MemoryDomain

    contentText: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)

    sourceType: str | None = None
    sourceId: str | None = None
    createdAt: datetime
    importanceScore: float = 0.5

    embeddingModelKey: str | None = None
    embedding: list[float] | None = None


class RetrievalScoreBreakdown(BaseModel):
    model_config = ConfigDict(extra="forbid")

    vector: float = 0.0
    lexical: float = 0.0
    recency: float = 0.0
    importance: float = 0.0
    domainBoost: float = 0.0
    total: float = 0.0


class RankedMemoryHit(BaseModel):
    model_config = ConfigDict(extra="forbid")

    memoryId: str
    domain: MemoryDomain
    contentText: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    score: RetrievalScoreBreakdown


class ContextSection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    domain: MemoryDomain
    summary: str
    references: list[str] = Field(default_factory=list)


class MemoryContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenantId: str
    workspaceId: str
    queryText: str
    mode: RetrievalMode
    generatedAt: datetime = Field(default_factory=datetime.utcnow)

    hits: list[RankedMemoryHit] = Field(default_factory=list)
    sections: list[ContextSection] = Field(default_factory=list)
    formattedContext: str = ""

