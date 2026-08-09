"""Tests for the indexing coordinator (event-driven, idempotent, replace-on-success)."""

import asyncio

from app.event_bus import InProcessEventBus, EventEnvelope

from ..chunking.fixed_size import FixedSizeChunker
from ..embedding.interface import EmbeddingError
from ..models.index_state import IndexState
from ..models.version import KnowledgeVersion
from ..storage.index_metadata import InMemoryIndexMetadataStore
from ..storage.in_memory_vector import InMemoryVectorStore
from ..indexing.coordinator import IndexingCoordinator


class FakeEmbeddingProvider:
    def __init__(self, *, fail: bool = False, model_id: str = "nomic-embed-text") -> None:
        self._fail = fail
        self._model_id = model_id

    @property
    def model_id(self) -> str:
        return self._model_id

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if self._fail:
            raise EmbeddingError("embedding down")
        return [[1.0, 0.0] for _ in texts]


def _make_version(
    *,
    document_id: str = "doc-1",
    content: str = "kora is a conductor and memory is separate",
    content_hash: str | None = None,
    version: str = "v1",
) -> KnowledgeVersion:
    return KnowledgeVersion(
        document_id=document_id,
        version=version,
        content_hash=content_hash or _hash(content),
        source=f"/src/{document_id}.md",
        content=content,
    )


def _hash(content: str) -> str:
    import hashlib

    return hashlib.sha256(content.encode()).hexdigest()


def _coordinator(*, embedder=None, event_bus=None):
    return IndexingCoordinator(
        chunker=FixedSizeChunker(size=16, overlap=2),
        embedding_provider=embedder or FakeEmbeddingProvider(),
        vector_store=InMemoryVectorStore(),
        metadata_store=InMemoryIndexMetadataStore(),
        event_bus=event_bus,
        indexing_event_topics=("knowledge.ingestion.file",),
    )


def test_index_version_creates_chunks_and_metadata():
    coordinator = _coordinator()
    version = _make_version()
    result = asyncio.run(coordinator.index_version(version))
    assert result.index_state == IndexState.INDEXED
    assert result.chunk_count > 0
    assert result.embedding_model == "nomic-embed-text"
    assert coordinator._metadata_store.get("doc-1").index_state == IndexState.INDEXED


def test_indexing_is_idempotent_for_same_version():
    coordinator = _coordinator()
    version = _make_version()
    first = asyncio.run(coordinator.index_version(version))
    second = asyncio.run(coordinator.index_version(version))
    assert first.chunk_ids == second.chunk_ids
    assert asyncio.run(coordinator._vector_store.count()) == first.chunk_count


def test_content_change_creates_new_version_and_retires_old():
    coordinator = _coordinator()
    v1 = _make_version(content="alpha version content", version="v1")
    asyncio.run(coordinator.index_version(v1))
    old_chunks = set(coordinator._metadata_store.get("doc-1").chunk_ids)

    v2 = _make_version(content="beta changed content here", version="v2")
    asyncio.run(coordinator.index_version(v2))
    meta = coordinator._metadata_store.get("doc-1")
    new_chunks = set(meta.chunk_ids)
    assert meta.version == "v2"
    assert meta.index_state == IndexState.INDEXED
    # Old chunks should be retired from the vector store.
    remaining = {r.id for r in asyncio.run(coordinator._vector_store.query([1.0, 0.0], top_k=100))}
    assert not (old_chunks & remaining)
    assert new_chunks & remaining


def test_embedding_failure_records_failed_state():
    coordinator = _coordinator(embedder=FakeEmbeddingProvider(fail=True))
    version = _make_version()
    result = asyncio.run(coordinator.index_version(version))
    assert result.index_state == IndexState.FAILED
    assert result.last_error is not None
    assert coordinator._metadata_store.get("doc-1").index_state == IndexState.FAILED


def test_event_driven_indexing():
    bus = InProcessEventBus()
    coordinator = _coordinator(event_bus=bus)

    async def scenario():
        envelope = EventEnvelope(
            event_type="knowledge.ingestion.file",
            source="test",
            payload={
                "document_id": "doc-e",
                "version": "v1",
                "content_hash": _hash("event content"),
                "source": "/src/event.md",
                "content": "event driven indexing content",
            },
        )
        bus.publish(envelope)
        # Let the scheduled async handler run.
        await asyncio.sleep(0.05)

    asyncio.run(scenario())
    meta = coordinator._metadata_store.get("doc-e")
    assert meta is not None
    assert meta.index_state == IndexState.INDEXED


def test_index_version_never_destroys_prior_index_on_failure():
    coordinator = _coordinator()
    v1 = _make_version(content="stable good content", version="v1")
    asyncio.run(coordinator.index_version(v1))
    good_meta = coordinator._metadata_store.get("doc-1")

    # Now a failing embedder should not invalidate the prior good index.
    coordinator._embedding = FakeEmbeddingProvider(fail=True)
    v2 = _make_version(content="changed but embedding fails", version="v2")
    asyncio.run(coordinator.index_version(v2))
    assert coordinator._metadata_store.get("doc-1").index_state == IndexState.FAILED
    # The vector store still holds the v1 chunks.
    remaining = {r.id for r in asyncio.run(coordinator._vector_store.query([1.0, 0.0], top_k=100))}
    assert set(good_meta.chunk_ids) <= remaining
