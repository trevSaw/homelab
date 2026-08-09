"""Tests for graph indexing coordinator (event-driven, idempotent, replace-on-success)."""

import asyncio

from app.event_bus import InProcessEventBus, EventEnvelope

from ..graph.indexing import GraphIndexingCoordinator, GraphIndexingError
from ..graph.in_memory_store import InMemoryGraphStore
from ..models.version import KnowledgeVersion


def _version(content: str, doc_id: str = "k1", version: str = "v1", content_hash: str | None = None):
    import hashlib

    return KnowledgeVersion(
        document_id=doc_id,
        version=version,
        content_hash=content_hash or hashlib.sha256(content.encode()).hexdigest(),
        source=f"/docs/{doc_id}.md",
        content=content,
    )


def test_index_creates_graph_representation():
    store = InMemoryGraphStore()
    coordinator = GraphIndexingCoordinator(graph_store=store)
    version = _version("# Architecture\n## Memory\n\nsee [[knowledge]]")
    asyncio.run(coordinator.index_version(version))
    assert store.list_entities()
    assert store.list_relationships()


def test_indexing_is_idempotent_for_same_version():
    store = InMemoryGraphStore()
    coordinator = GraphIndexingCoordinator(graph_store=store)
    version = _version("stable content with a link [[other]]")
    asyncio.run(coordinator.index_version(version))
    first_entities = len(store.list_entities())
    asyncio.run(coordinator.index_version(version))
    assert len(store.list_entities()) == first_entities


def test_updated_version_replaces_stale_graph_data():
    store = InMemoryGraphStore()
    coordinator = GraphIndexingCoordinator(graph_store=store)
    v1 = _version("# V1\n\nreferences [old](./old.md)")
    asyncio.run(coordinator.index_version(v1))
    old_entity_ids = {e.entity_id for e in store.list_entities()}
    old_rel_ids = {r.relationship_id for r in store.list_relationships()}

    v2 = _version("# V2\n\nreferences [new](./new.md)", version="v2")
    asyncio.run(coordinator.index_version(v2))
    new_entity_ids = {e.entity_id for e in store.list_entities()}
    new_rel_ids = {r.relationship_id for r in store.list_relationships()}
    assert not (old_rel_ids & new_rel_ids)
    assert "old" not in " ".join(e.canonical_name for e in store.list_entities())


def test_event_driven_indexing():
    bus = InProcessEventBus()
    store = InMemoryGraphStore()
    coordinator = GraphIndexingCoordinator(graph_store=store, event_bus=bus)

    async def scenario():
        bus.publish(
            EventEnvelope(
                event_type="knowledge.ingestion.file",
                source="test",
                payload={
                    "document_id": "k9",
                    "version": "v1",
                    "content_hash": "abc",
                    "source": "/docs/k9.md",
                    "content": "# Doc\n\ntalks about [[memory]]",
                },
            )
        )
        await asyncio.sleep(0.05)

    asyncio.run(scenario())
    assert store.list_entities()
    coordinator.close()


def test_unrelated_events_do_not_trigger_graph_indexing():
    bus = InProcessEventBus()
    store = InMemoryGraphStore()
    coordinator = GraphIndexingCoordinator(graph_store=store, event_bus=bus)

    async def scenario():
        bus.publish(
            EventEnvelope(
                event_type="memory.candidate",
                source="memory-runtime",
                payload={"candidate_type": "user"},
            )
        )
        await asyncio.sleep(0.05)

    asyncio.run(scenario())
    assert store.list_entities() == []
    coordinator.close()


def test_graph_indexing_failure_does_not_invalidate_knowledge():
    class FailingStore(InMemoryGraphStore):
        def upsert_entity(self, entity):
            raise RuntimeError("graph backend down")

    store = FailingStore()
    coordinator = GraphIndexingCoordinator(graph_store=store)
    version = _version("some content")
    try:
        asyncio.run(coordinator.index_version(version))
        assert False, "expected GraphIndexingError"
    except GraphIndexingError:
        pass
    # Authoritative Knowledge is unaffected (the store only holds derived graph).
