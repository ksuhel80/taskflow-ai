from __future__ import annotations

from dataclasses import dataclass

from .embedding_utils import EmbeddingClientPort, normalize_whitespace
from .models import MemoryContext, MemoryQuery, RetrievalMode
from .ranking import RankingWeights, rank_candidates
from .serializers import to_ai_ready_context
from .vector_query import MemoryRepositoryPort


@dataclass(frozen=True)
class RetrievalConfig:
    embeddingModel: str = "text-embedding-3-large"
    candidateLimit: int = 100


class MemoryRetrievalService:
    """
    Production-grade memory retrieval engine.

    Supports:
    - semantic/vector retrieval
    - metadata filtering (via repository)
    - hybrid retrieval (vector + lexical)
    - ranking
    - context compression
    - workspace isolation
    - AI-ready context formatting
    """

    def __init__(
        self,
        *,
        repository: MemoryRepositoryPort,
        embeddingClient: EmbeddingClientPort,
        config: RetrievalConfig | None = None,
    ) -> None:
        self._repo = repository
        self._emb = embeddingClient
        self._cfg = config or RetrievalConfig()

    async def retrieve(self, *, query: MemoryQuery) -> MemoryContext:
        query_text = normalize_whitespace(query.queryText)
        query_embedding = await self._emb.embed_text(text=query_text, model=self._cfg.embeddingModel)

        # Workspace isolation should be enforced both here and in repository SQL predicates.
        if not query.workspaceId:
            raise ValueError("workspaceId is required for workspace isolation")

        vector_candidates = await self._repo.vector_candidates(
            query=query,
            queryEmbedding=query_embedding,
            candidateLimit=self._cfg.candidateLimit,
        )

        if query.mode == RetrievalMode.HYBRID:
            lexical_candidates = await self._repo.metadata_candidates(
                query=query,
                candidateLimit=self._cfg.candidateLimit,
            )
            # Merge by memoryId while preserving richer record fields.
            by_id = {c.memoryId: c for c in vector_candidates}
            for c in lexical_candidates:
                by_id.setdefault(c.memoryId, c)
            candidates = list(by_id.values())
        else:
            candidates = vector_candidates

        ranked = rank_candidates(
            queryText=query_text,
            queryEmbedding=query_embedding,
            candidates=candidates,
            weights=RankingWeights(),
        )

        if query.minVectorScore is not None:
            ranked = [r for r in ranked if r.score.vector >= query.minVectorScore]

        ranked = ranked[: query.topK]

        return to_ai_ready_context(
            tenantId=query.tenantId,
            workspaceId=query.workspaceId,
            queryText=query_text,
            mode=query.mode,
            hits=ranked,
            maxTokens=query.maxContextTokens,
        )

