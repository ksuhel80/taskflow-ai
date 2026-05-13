from __future__ import annotations

from collections import defaultdict

from .models import ContextSection, MemoryContext, MemoryDomain, RankedMemoryHit


def estimate_tokens(text: str) -> int:
    # Rough approximation: ~4 chars/token for English-like text.
    return max(1, len(text) // 4)


def compress_hits_for_budget(*, hits: list[RankedMemoryHit], maxTokens: int) -> list[RankedMemoryHit]:
    compressed: list[RankedMemoryHit] = []
    used = 0
    for hit in hits:
        t = estimate_tokens(hit.contentText)
        if used + t <= maxTokens:
            compressed.append(hit)
            used += t
            continue

        # If full text doesn't fit, include truncated fragment when still useful.
        remaining = maxTokens - used
        if remaining <= 20:
            break
        approx_chars = remaining * 4
        truncated = hit.model_copy(
            update={
                "contentText": hit.contentText[:approx_chars].rstrip() + " ...",
            }
        )
        compressed.append(truncated)
        break
    return compressed


def build_sections(*, hits: list[RankedMemoryHit]) -> list[ContextSection]:
    grouped: dict[MemoryDomain, list[RankedMemoryHit]] = defaultdict(list)
    for h in hits:
        grouped[h.domain].append(h)

    ordered = [MemoryDomain.PREFERENCE, MemoryDomain.DECISION, MemoryDomain.SEMANTIC]
    sections: list[ContextSection] = []
    for domain in ordered:
        domain_hits = grouped.get(domain, [])
        if not domain_hits:
            continue
        refs = [h.memoryId for h in domain_hits]
        summary_parts = [f"- {h.contentText}" for h in domain_hits]
        sections.append(
            ContextSection(
                title=f"{domain.value.title()} Memory",
                domain=domain,
                summary="\n".join(summary_parts),
                references=refs,
            )
        )
    return sections


def format_context_markdown(*, sections: list[ContextSection]) -> str:
    if not sections:
        return "No relevant memory context found."
    out: list[str] = ["# Memory Context"]
    for sec in sections:
        out.append(f"\n## {sec.title}\n{sec.summary}\n")
        out.append(f"References: {', '.join(sec.references)}")
    return "\n".join(out).strip()


def to_ai_ready_context(
    *,
    tenantId: str,
    workspaceId: str,
    queryText: str,
    mode,
    hits: list[RankedMemoryHit],
    maxTokens: int,
) -> MemoryContext:
    compressed_hits = compress_hits_for_budget(hits=hits, maxTokens=maxTokens)
    sections = build_sections(hits=compressed_hits)
    formatted = format_context_markdown(sections=sections)
    return MemoryContext(
        tenantId=tenantId,
        workspaceId=workspaceId,
        queryText=queryText,
        mode=mode,
        hits=compressed_hits,
        sections=sections,
        formattedContext=formatted,
    )

