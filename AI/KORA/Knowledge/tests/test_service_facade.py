"""Tests for Knowledge versioning and the Knowledge Service facade."""

import asyncio

from app.event_bus import InProcessEventBus

from ..config import KnowledgeConfig
from ..models.document import KnowledgeDocument
from ..models.index_state import IndexState
from ..models.version import KnowledgeVersion, document_id_from_source, sha256_hex
from ..service import KnowledgeService, build_knowledge_service
from ..storage.in_memory import InMemoryKnowledgeStore
from ..storage.in_memory_vector import InMemoryVectorStore
from ..storage.index_metadata import InMemoryIndexMetadataStore


def test_document_id_stable_from_source():
    a = document_id_from_source("/src/a.md")
    b = document_id_from_source("/src/a.md")
    c = document_id_from_source("/src/b.md")
    assert a == b
    assert a != c


def test_content_hash_deterministic():
    assert sha256_hex("same") == sha256_hex("same")
    assert sha256_hex("same") != sha256_hex("different")


def test_version_from_document():
    doc = KnowledgeDocument(content="hello world", source="/src/a.md", metadata={"t": "1"})
    version = KnowledgeVersion.from_document(doc)
    assert version.content_hash == doc.doc_id
    assert version.document_id == document_id_from_source("/src/a.md")
    assert version.content == "hello world"


def test_version_unchanged_for_same_content():
    doc1 = KnowledgeDocument(content="same text", source="/src/a.md")
    doc2 = KnowledgeDocument(content="same text", source="/src/a.md")
    v1 = KnowledgeVersion.from_document(doc1)
    v2 = KnowledgeVersion.from_document(doc2)
    assert v1.content_hash == v2.content_hash
    assert v1.version == v2.version


def _config(tmp_path) -> KnowledgeConfig:
    return KnowledgeConfig(
        vector_provider="in_memory",
        index_metadata_sqlite_enabled=False,
        embedding_base_url="http://ollama:11434",
        embedding_model="nomic-embed-text",
        chunk_size=16,
        chunk_overlap=2,
    )


def _fake_embedder():
    class Fake:
        @property
        def model_id(self) -> str:
            return "nomic-embed-text"

        async def embed(self, texts: list[str]) -> list[list[float]]:
            return [[1.0, 0.0] for _ in texts]

    return Fake()


def test_service_ingest_then_index(tmp_path):
    bus = InProcessEventBus()
    store = InMemoryKnowledgeStore()
    service = KnowledgeService(
        config=_config(tmp_path),
        store=store,
        event_bus=bus,
        embedding_provider=_fake_embedder(),
        vector_store=InMemoryVectorStore(),
        index_metadata=InMemoryIndexMetadataStore(),
    )
    file_path = tmp_path / "doc.md"
    file_path.write_text("kora is a conductor and memory is separate")
    version = asyncio.run(service.ingest_file(str(file_path)))
    assert version.document_id
    # Index explicitly (the event-driven path is covered separately).
    meta = asyncio.run(service.index_version(version))
    assert meta.index_state == IndexState.INDEXED
    result = asyncio.run(service.retrieve("kora"))
    assert result.results


def test_build_knowledge_service_composes(tmp_path):
    bus = InProcessEventBus()
    store = InMemoryKnowledgeStore()
    service = build_knowledge_service(
        config=_config(tmp_path),
        store=store,
        event_bus=bus,
        embedding_transport=None,
        vector_transport=None,
    )
    assert isinstance(service, KnowledgeService)
    assert service.retrieval.top_k == 5
