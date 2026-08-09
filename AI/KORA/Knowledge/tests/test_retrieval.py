"""Tests for the Knowledge retrieval service and context assembly."""

import asyncio

from ..context.assembly import KnowledgeContextAssembler
from ..embedding.interface import EmbeddingError
from ..retrieval.service import KnowledgeRetrievalService
from ..storage.in_memory_vector import InMemoryVectorStore


class FakeEmbeddingProvider:
    @property
    def model_id(self) -> str:
        return "nomic-embed-text"

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [[1.0, 0.0, 0.0] for _ in texts]


class FailingEmbeddingProvider:
    @property
    def model_id(self) -> str:
        return "fail"

    async def embed(self, texts: list[str]) -> list[list[float]]:
        raise EmbeddingError("down")


def _service(*, embedder=None, top_k=3):
    return KnowledgeRetrievalService(
        embedding_provider=embedder or FakeEmbeddingProvider(),
        vector_store=InMemoryVectorStore(),
        top_k=top_k,
        backend_name="chroma",
    )


def _seed(store):
    asyncio.run(
        store.upsert(
            ["d1:v1:0", "d2:v1:0"],
            [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
            ["kora is a conductor", "memory is separate"],
            [
                {"document_id": "d1", "document_version": "v1", "content_hash": "h1", "source": "s1"},
                {"document_id": "d2", "document_version": "v1", "content_hash": "h2", "source": "s2"},
            ],
        )
    )


def test_retrieval_returns_provenance():
    store = InMemoryVectorStore()
    _seed(store)
    service = KnowledgeRetrievalService(
        embedding_provider=FakeEmbeddingProvider(), vector_store=store, top_k=2
    )
    result = asyncio.run(service.retrieve("kora"))
    assert result.status == "ok"
    assert result.results
    chunk = result.results[0]
    assert chunk.document_id == "d1"
    assert chunk.document_version == "v1"
    assert chunk.source == "s1"
    assert chunk.content_hash == "h1"


def test_retrieval_top_k_respected():
    store = InMemoryVectorStore()
    _seed(store)
    service = KnowledgeRetrievalService(
        embedding_provider=FakeEmbeddingProvider(), vector_store=store, top_k=1
    )
    result = asyncio.run(service.retrieve("kora"))
    assert len(result.results) == 1


def test_retrieval_empty_returns_ok_empty():
    store = InMemoryVectorStore()
    service = _service()
    result = asyncio.run(service.retrieve("nothing to find"))
    assert result.status == "ok"
    assert result.results == []


def test_retrieval_backend_failure_degrades():
    service = KnowledgeRetrievalService(
        embedding_provider=FailingEmbeddingProvider(),
        vector_store=InMemoryVectorStore(),
        top_k=2,
    )
    result = asyncio.run(service.retrieve("kora"))
    assert result.status == "degraded"
    assert result.results == []


def test_context_assembly_includes_sources_and_text():
    store = InMemoryVectorStore()
    _seed(store)
    service = KnowledgeRetrievalService(
        embedding_provider=FakeEmbeddingProvider(), vector_store=store, top_k=2
    )
    assembler = KnowledgeContextAssembler(retrieval_service=service, top_k=2)
    context = asyncio.run(assembler.build_context("kora"))
    assert context.status == "ok"
    assert "d1" in context.sources
    assert "kora is a conductor" in context.knowledge_text
    assert context.chunks


def test_context_assembly_degraded_returns_empty_text():
    service = KnowledgeRetrievalService(
        embedding_provider=FailingEmbeddingProvider(),
        vector_store=InMemoryVectorStore(),
        top_k=2,
    )
    assembler = KnowledgeContextAssembler(retrieval_service=service, top_k=2)
    context = asyncio.run(assembler.build_context("kora"))
    assert context.status == "degraded"
    assert context.knowledge_text == ""
