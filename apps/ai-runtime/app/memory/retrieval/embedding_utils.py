from __future__ import annotations

from typing import Protocol


class EmbeddingClientPort(Protocol):
    """
    Abstraction for embedding providers (OpenAI, LiteLLM proxy, etc.).
    """

    async def embed_text(self, *, text: str, model: str) -> list[float]: ...


def l2_norm(vec: list[float]) -> float:
    return sum(v * v for v in vec) ** 0.5


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    denom = l2_norm(a) * l2_norm(b)
    if denom == 0:
        return 0.0
    # Normalize from [-1,1] to [0,1] for easier ranking composition.
    raw = dot / denom
    return (raw + 1.0) / 2.0


def normalize_whitespace(text: str) -> str:
    return " ".join(text.split())

