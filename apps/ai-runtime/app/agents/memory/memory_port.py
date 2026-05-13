from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field


class MemoryQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenantId: str
    namespaceType: str
    namespaceKey: str
    queryText: str

    topK: int = 5
    minScore: float | None = None


class MemoryHit(BaseModel):
    model_config = ConfigDict(extra="forbid")

    itemId: str
    score: float
    contentPreview: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class MemoryContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenantId: str
    namespaceType: str
    namespaceKey: str

    retrievedAt: datetime = Field(default_factory=datetime.utcnow)
    hits: list[MemoryHit] = Field(default_factory=list)


class MemoryRetrieverPort(Protocol):
    async def retrieve(self, *, query: MemoryQuery) -> MemoryContext: ...

