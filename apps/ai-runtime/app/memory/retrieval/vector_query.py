from __future__ import annotations

from typing import Protocol

from .models import MemoryQuery, MemoryRecord


class MemoryRepositoryPort(Protocol):
    """
    Persistence abstraction (PostgreSQL + pgvector + Prisma-backed service).

    Implementations should enforce workspace isolation server-side as well.
    """

    async def vector_candidates(
        self,
        *,
        query: MemoryQuery,
        queryEmbedding: list[float],
        candidateLimit: int,
    ) -> list[MemoryRecord]: ...

    async def metadata_candidates(
        self,
        *,
        query: MemoryQuery,
        candidateLimit: int,
    ) -> list[MemoryRecord]: ...


def keyword_tokens(text: str) -> set[str]:
    return {tok.strip().lower() for tok in text.split() if tok.strip()}


def lexical_overlap_score(*, queryText: str, candidateText: str) -> float:
    q = keyword_tokens(queryText)
    c = keyword_tokens(candidateText)
    if not q or not c:
        return 0.0
    overlap = len(q.intersection(c))
    return overlap / len(q)

