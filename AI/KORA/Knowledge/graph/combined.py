"""Combined Knowledge retrieval: semantic (Chroma) + graph (GraphStore).

The orchestration layer decides when graph retrieval is useful, without
hard-wiring Chroma and Graphify together.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from ..retrieval.service import KnowledgeRetrievalService
from .retrieval import GraphRetrievalResult, GraphRetrievalService

log = logging.getLogger("kora.knowledge.graph.combined")


@dataclass(frozen=True, slots=True)
class CombinedRetrievalResult:
    query: str
    status: str  # "ok" | "degraded"
    semantic: dict[str, Any]
    graph: GraphRetrievalResult

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "status": self.status,
            "semantic": self.semantic,
            "graph": self.graph.to_dict(),
        }


class CombinedRetrievalService:
    """Orchestrates semantic and graph retrieval.

    The graph pass runs only when the caller requests it (graph_enabled) and
    degrades to semantic-only when the graph backend is unavailable.
    """

    def __init__(
        self,
        *,
        semantic: KnowledgeRetrievalService,
        graph: GraphRetrievalService,
        graph_enabled: bool = True,
    ) -> None:
        self._semantic = semantic
        self._graph = graph
        self._graph_enabled = graph_enabled

    async def retrieve(
        self,
        query: str,
        *,
        top_k: int | None = None,
        graph_top_k: int | None = None,
    ) -> CombinedRetrievalResult:
        semantic_result = await self._semantic.retrieve(query, top_k=top_k)
        graph_result = await self._retrieve_graph(query, top_k=graph_top_k)
        status = "ok" if semantic_result.status == "ok" else "degraded"
        return CombinedRetrievalResult(
            query=query,
            status=status,
            semantic=semantic_result.to_dict(),
            graph=graph_result,
        )

    async def _retrieve_graph(self, query: str, *, top_k: int | None) -> GraphRetrievalResult:
        if not self._graph_enabled:
            return GraphRetrievalResult(
                query, "degraded", "graph_disabled", entities=(), relationships=()
            )
        # Try the full query first (matches hyphenated canonical names), then
        # fall back to a single token candidate.
        result = await self._graph.lookup_entity(query)
        if not result.entities:
            entity_name = _first_entity_candidate(query)
            result = await self._graph.lookup_entity(entity_name)
        if result.status == "degraded":
            # Fall back to a neighbor sweep for the first matched entity if any.
            if result.entities:
                return await self._graph.neighbors(result.entities[0].entity_id)
        return result


def _first_entity_candidate(query: str) -> str:
    stopwords = {
        "what", "is", "are", "the", "a", "an", "how", "does", "do", "which",
        "where", "when", "who", "why", "can", "kora", "memory", "knowledge",
        "and", "or", "of", "to", "in", "for", "with", "about", "between",
        "relationship", "relate", "related", "architecture", "graph",
    }
    tokens = [t.strip(".,!?()[]{}:;\"'") for t in query.split()]
    for token in tokens:
        lower = token.lower()
        if lower and lower not in stopwords and len(token) >= 3:
            return token
    return query.strip()
