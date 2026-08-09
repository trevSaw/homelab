"""Graph-aware context assembly.

Composes semantic Knowledge evidence and graph (relationship) evidence into a
single provenance-labeled context block for the LLM. Graph-derived claims remain
traceable to authoritative Knowledge. This extends—not replaces—the Phase 14.3
context system.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..graph.combined import CombinedRetrievalService


@dataclass(frozen=True, slots=True)
class GraphKnowledgeContext:
    query: str
    status: str
    knowledge_sources: tuple[str, ...]
    graph_entities: tuple[dict[str, Any], ...]
    graph_relationships: tuple[dict[str, Any], ...]
    text: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "status": self.status,
            "knowledge_sources": list(self.knowledge_sources),
            "graph_entities": list(self.graph_entities),
            "graph_relationships": list(self.graph_relationships),
            "text": self.text,
        }


class GraphContextAssembler:
    def __init__(
        self,
        *,
        combined: CombinedRetrievalService,
        top_k: int = 5,
        max_chars: int = 8000,
    ) -> None:
        self._combined = combined
        self._top_k = max(1, top_k)
        self._max_chars = max(0, max_chars)

    async def build_context(self, query: str, *, top_k: int | None = None) -> GraphKnowledgeContext:
        result = await self._combined.retrieve(query, top_k=top_k or self._top_k)
        semantic = result.semantic or {}
        chunks = semantic.get("results") or []
        knowledge_sources = tuple(
            {chunk.get("document_id") for chunk in chunks if chunk.get("document_id")}
        )
        graph_entities = tuple(e.to_dict() for e in result.graph.entities)
        graph_relationships = tuple(r.to_dict() for r in result.graph.relationships)
        text = _render(
            chunks=chunks,
            entities=graph_entities,
            relationships=graph_relationships,
            max_chars=self._max_chars,
        )
        return GraphKnowledgeContext(
            query=query,
            status=result.status,
            knowledge_sources=knowledge_sources,
            graph_entities=graph_entities,
            graph_relationships=graph_relationships,
            text=text,
        )


def _render(
    *,
    chunks: list[dict[str, Any]],
    entities: tuple[dict[str, Any], ...],
    relationships: tuple[dict[str, Any], ...],
    max_chars: int,
) -> str:
    if not chunks and not relationships:
        return ""
    parts: list[str] = []
    budget = max_chars

    if chunks:
        knowledge_block = "\n\n".join(
            f"[Knowledge: {chunk.get('document_id', 'unknown')} "
            f"v{chunk.get('document_version', '?')}]\n{chunk.get('content', '')}"
            for chunk in chunks
        )
        if budget > 0:
            parts.append(knowledge_block[:budget])
            budget -= len(knowledge_block)

    if relationships:
        rel_lines: list[str] = []
        for rel in relationships:
            source = rel.get("source_entity", "?")
            rel_type = rel.get("relationship_type", "?")
            target = rel.get("target_entity", "?")
            knowledge_id = rel.get("source_knowledge_id", "")
            rel_lines.append(
                f"{source} --{rel_type}--> {target} "
                f"[knowledge={knowledge_id[:12]}]"
            )
        graph_block = "[Graph relationships]\n" + "\n".join(rel_lines)
        if budget > 0:
            parts.append(graph_block[:budget])

    return "\n\n".join(parts)
