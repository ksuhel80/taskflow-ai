from __future__ import annotations

from datetime import datetime, timezone

from .embedding_utils import cosine_similarity
from .models import MemoryDomain, MemoryRecord, RankedMemoryHit, RetrievalScoreBreakdown
from .vector_query import lexical_overlap_score


class RankingWeights:
    def __init__(
        self,
        *,
        vector: float = 0.55,
        lexical: float = 0.2,
        recency: float = 0.15,
        importance: float = 0.1,
    ) -> None:
        self.vector = vector
        self.lexical = lexical
        self.recency = recency
        self.importance = importance


def recency_score(created_at: datetime, *, half_life_days: int = 14) -> float:
    now = datetime.now(timezone.utc)
    created = created_at if created_at.tzinfo else created_at.replace(tzinfo=timezone.utc)
    age_days = max((now - created).total_seconds() / 86_400.0, 0.0)
    # Exponential decay mapped to [0,1].
    return 0.5 ** (age_days / max(half_life_days, 1))


def domain_boost(domain: MemoryDomain) -> float:
    # Preferences and decisions should usually have stronger influence on behavior.
    if domain == MemoryDomain.PREFERENCE:
        return 0.08
    if domain == MemoryDomain.DECISION:
        return 0.05
    return 0.0


def rank_candidates(
    *,
    queryText: str,
    queryEmbedding: list[float],
    candidates: list[MemoryRecord],
    weights: RankingWeights | None = None,
) -> list[RankedMemoryHit]:
    w = weights or RankingWeights()
    ranked: list[RankedMemoryHit] = []

    for c in candidates:
        vector = cosine_similarity(queryEmbedding, c.embedding or [])
        lexical = lexical_overlap_score(queryText=queryText, candidateText=c.contentText)
        recency = recency_score(c.createdAt)
        importance = min(max(c.importanceScore, 0.0), 1.0)
        boost = domain_boost(c.domain)

        total = (w.vector * vector) + (w.lexical * lexical) + (w.recency * recency) + (w.importance * importance) + boost

        breakdown = RetrievalScoreBreakdown(
            vector=vector,
            lexical=lexical,
            recency=recency,
            importance=importance,
            domainBoost=boost,
            total=total,
        )
        ranked.append(
            RankedMemoryHit(
                memoryId=c.memoryId,
                domain=c.domain,
                contentText=c.contentText,
                metadata=c.metadata,
                score=breakdown,
            )
        )

    ranked.sort(key=lambda x: x.score.total, reverse=True)
    return ranked

