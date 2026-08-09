"""Knowledge-to-context boundary.

Transforms retrieved Knowledge into provenance-labeled context suitable for the
LLM. Kept separate from Memory, Council reasoning, Tool execution, and graph
reasoning.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..retrieval.service import KnowledgeRetrievalService


@dataclass(frozen=True, slots=True)
class KnowledgeContext:
    query: str
    status: str
    sources: tuple[str, ...]
    chunks: tuple[dict[str, Any], ...]
    knowledge_text: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "status": self.status,
            "sources": list(self.sources),
            "chunks": list(self.chunks),
            "knowledge_text": self.knowledge_text,
        }


class KnowledgeContextAssembler:
    def __init__(
        self,
        *,
        retrieval_service: KnowledgeRetrievalService,
        top_k: int = 5,
        max_chars: int = 8000,
    ) -> None:
        self._retrieval = retrieval_service
        self._top_k = max(1, top_k)
        self._max_chars = max(0, max_chars)

    async def build_context(self, query: str, *, top_k: int | None = None) -> KnowledgeContext:
        result = await self._retrieval.retrieve(query, top_k=top_k or self._top_k)
        chunks = [chunk.to_dict() for chunk in result.results]
        sources = tuple({chunk["document_id"] for chunk in chunks if chunk["document_id"]})
        knowledge_text = _render(chunks, max_chars=self._max_chars)
        return KnowledgeContext(
            query=query,
            status=result.status,
            sources=sources,
            chunks=tuple(chunks),
            knowledge_text=knowledge_text,
        )


def _render(chunks: list[dict[str, Any]], *, max_chars: int) -> str:
    if not chunks:
        return ""
    parts: list[str] = []
    budget = max_chars
    for chunk in chunks:
        header = (
            f"[Source: {chunk.get('document_id', 'unknown')} "
            f"v{chunk.get('document_version', '?')} | {chunk.get('source', 'unknown')}]"
        )
        block = f"{header}\n{chunk.get('content', '')}"
        if budget <= 0:
            break
        if len(block) > budget:
            parts.append(block[:budget])
            budget = 0
        else:
            parts.append(block)
            budget -= len(block)
    return "\n\n".join(parts)
