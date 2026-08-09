"""KORA-owned Knowledge retrieval service.

The Runtime requests relevant Knowledge through this service without knowing
Chroma implementation details. Results preserve provenance: every returned chunk
traces back to its authoritative document id, version, content hash, and source.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from ..embedding.interface import EmbeddingError, EmbeddingProvider
from ..storage.vector import VectorStore, VectorStoreError

log = logging.getLogger("kora.knowledge.retrieval")


class RetrievalBackendError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class RetrievedChunk:
    chunk_id: str
    document_id: str
    document_version: str
    content_hash: str
    source: str
    content: str
    metadata: dict[str, Any]
    distance: float
    score: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "document_version": self.document_version,
            "content_hash": self.content_hash,
            "source": self.source,
            "content": self.content,
            "metadata": self.metadata,
            "distance": self.distance,
            "score": self.score,
        }


@dataclass(frozen=True, slots=True)
class KnowledgeRetrievalResult:
    query: str
    results: list[RetrievedChunk]
    status: str  # "ok" | "degraded"
    backend: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "status": self.status,
            "backend": self.backend,
            "results": [chunk.to_dict() for chunk in self.results],
        }


class KnowledgeRetrievalService:
    def __init__(
        self,
        *,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
        top_k: int = 5,
        backend_name: str = "chroma",
    ) -> None:
        self._embedding = embedding_provider
        self._vector_store = vector_store
        self._top_k = max(1, top_k)
        self._backend_name = backend_name

    @property
    def top_k(self) -> int:
        return self._top_k

    async def retrieve(
        self,
        query: str,
        *,
        top_k: int | None = None,
        where: dict[str, Any] | None = None,
    ) -> KnowledgeRetrievalResult:
        if not query.strip():
            return KnowledgeRetrievalResult(query=query, results=[], status="ok", backend=self._backend_name)
        try:
            vectors = await self._embedding.embed([query])
            query_vector = vectors[0]
            raw = await self._vector_store.query(
                query_vector,
                top_k=top_k or self._top_k,
                where=where,
            )
        except (EmbeddingError, VectorStoreError, RetrievalBackendError) as exc:
            log.warning("knowledge retrieval degraded: %s", exc)
            return KnowledgeRetrievalResult(
                query=query, results=[], status="degraded", backend=self._backend_name
            )
        results = [_to_retrieved_chunk(item) for item in raw]
        return KnowledgeRetrievalResult(
            query=query, results=results, status="ok", backend=self._backend_name
        )


def _to_retrieved_chunk(item: Any) -> RetrievedChunk:
    metadata = item.metadata or {}
    distance = float(item.distance or 0.0)
    return RetrievedChunk(
        chunk_id=str(item.id),
        document_id=str(metadata.get("document_id", "")),
        document_version=str(metadata.get("document_version", "")),
        content_hash=str(metadata.get("content_hash", "")),
        source=str(metadata.get("source", "")),
        content=str(item.document),
        metadata=metadata,
        distance=distance,
        score=_score(distance),
    )


def _score(distance: float) -> float:
    # Chroma cosine distance ∈ [0, 2]; map to a 0..1 similarity score.
    return max(0.0, min(1.0, 1.0 - distance / 2.0))
