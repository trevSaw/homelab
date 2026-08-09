"""Tests for graph retrieval, combined retrieval, and graph context assembly."""

import asyncio

from ..graph.combined import CombinedRetrievalService
from ..graph.in_memory_store import InMemoryGraphStore
from ..graph.models import GraphEntity, GraphRelationship, entity_id, relationship_id
from ..graph.retrieval import GraphRetrievalService
from ..context.graph_context import GraphContextAssembler
from ..retrieval.service import KnowledgeRetrievalService
from ..storage.in_memory_vector import InMemoryVectorStore


class _FakeEmbedding:
    @property
    def model_id(self) -> str:
        return "nomic-embed-text"

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [[1.0, 0.0, 0.0] for _ in texts]


def _seed_graph():
    store = InMemoryGraphStore()
    a = GraphEntity(
        entity_id=entity_id("memory-service", "document"),
        entity_type="document",
        canonical_name="memory-service",
        source_knowledge_id="k1",
        source_version="v1",
        source_content_hash="h1",
        source_ref="/docs/memory.md",
    )
    b = GraphEntity(
        entity_id=entity_id("knowledge-service", "document"),
        entity_type="document",
        canonical_name="knowledge-service",
        source_knowledge_id="k2",
        source_version="v1",
        source_content_hash="h2",
        source_ref="/docs/knowledge.md",
    )
    store.upsert_entity(a)
    store.upsert_entity(b)
    store.upsert_relationship(
        GraphRelationship(
            relationship_id=relationship_id(a.entity_id, "references", b.entity_id),
            source_entity=a.entity_id,
            relationship_type="references",
            target_entity=b.entity_id,
            source_knowledge_id="k1",
            confidence="EXTRACTED",
        )
    )
    return store, a, b


def test_graph_lookup_entity_returns_provenance():
    store, a, b = _seed_graph()
    service = GraphRetrievalService(graph_store=store)
    result = asyncio.run(service.lookup_entity("memory-service"))
    assert result.status == "ok"
    assert any(e.source_knowledge_id == "k1" for e in result.entities)
    assert any(r.relationship_type == "references" for r in result.relationships)


def test_graph_neighbors():
    store, a, b = _seed_graph()
    service = GraphRetrievalService(graph_store=store)
    result = asyncio.run(service.neighbors(a.entity_id))
    assert any(e.entity_id == b.entity_id for e in result.entities)


def test_graph_lookup_empty():
    store = InMemoryGraphStore()
    service = GraphRetrievalService(graph_store=store)
    result = asyncio.run(service.lookup_entity("nothing"))
    assert result.status == "ok"
    assert result.entities == ()
    assert result.relationships == ()


class _FailingGraphStore(InMemoryGraphStore):
    def find_entities_by_name(self, name: str):
        raise RuntimeError("graph down")


def test_graph_lookup_degraded_on_failure():
    service = GraphRetrievalService(graph_store=_FailingGraphStore())
    result = asyncio.run(service.lookup_entity("memory"))
    assert result.status == "degraded"
    assert result.entities == ()


def _semantic_service():
    vector = InMemoryVectorStore()
    asyncio.run(
        vector.upsert(
            ["k1:v1:0"],
            [[1.0, 0.0, 0.0]],
            ["memory service details"],
            [{"document_id": "k1", "document_version": "v1"}],
        )
    )
    return KnowledgeRetrievalService(
        embedding_provider=_FakeEmbedding(), vector_store=vector, top_k=2
    )


def test_combined_retrieval_combines_semantic_and_graph():
    store, a, b = _seed_graph()
    combined = CombinedRetrievalService(
        semantic=_semantic_service(),
        graph=GraphRetrievalService(graph_store=store),
        graph_enabled=True,
    )
    result = asyncio.run(combined.retrieve("memory service"))
    assert result.status == "ok"
    assert result.semantic["results"]  # semantic chunks
    assert result.graph.relationships  # graph relationships


def test_combined_retrieval_graph_disabled():
    store, a, b = _seed_graph()
    combined = CombinedRetrievalService(
        semantic=_semantic_service(),
        graph=GraphRetrievalService(graph_store=store),
        graph_enabled=False,
    )
    result = asyncio.run(combined.retrieve("memory"))
    assert result.graph.entities == ()
    assert result.graph.status == "degraded"


def test_graph_context_assembly_includes_provenance():
    store, a, b = _seed_graph()
    combined = CombinedRetrievalService(
        semantic=_semantic_service(),
        graph=GraphRetrievalService(graph_store=store),
        graph_enabled=True,
    )
    assembler = GraphContextAssembler(combined=combined, top_k=2)
    context = asyncio.run(assembler.build_context("memory service"))
    assert context.status == "ok"
    assert context.knowledge_sources
    assert "Graph relationships" in context.text or context.graph_relationships
