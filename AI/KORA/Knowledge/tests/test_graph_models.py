"""Tests for the graph data model and GraphStore implementations."""

import tempfile

from ..graph.models import GraphEntity, GraphRelationship, entity_id, relationship_id
from ..graph.in_memory_store import InMemoryGraphStore
from ..graph.sqlite_store import SQLiteGraphStore


def test_entity_identity_is_deterministic():
    a = entity_id("Memory Service", "document")
    b = entity_id("Memory Service", "document")
    c = entity_id("Memory Service", "concept")
    assert a == b
    assert a != c


def test_relationship_identity_is_deterministic():
    a = relationship_id("e1", "references", "e2")
    b = relationship_id("e1", "references", "e2")
    assert a == b
    assert a != relationship_id("e1", "contains", "e2")


def test_entity_provenance():
    entity = GraphEntity(
        entity_id="e1",
        entity_type="document",
        canonical_name="architecture.md",
        source_knowledge_id="k1",
        source_version="v1",
        source_content_hash="abc",
        source_ref="/docs/architecture.md",
    )
    assert entity.source_knowledge_id == "k1"
    assert entity.source_version == "v1"
    assert entity.source_content_hash == "abc"


def _sample_entity(name="memory-service", etype="document", kid="k1"):
    return GraphEntity(
        entity_id=entity_id(name, etype),
        entity_type=etype,
        canonical_name=name,
        source_knowledge_id=kid,
        source_version="v1",
        source_content_hash="h1",
        source_ref=f"/docs/{name}.md",
    )


def _sample_relationship(src, rel, tgt, kid="k1"):
    return GraphRelationship(
        relationship_id=relationship_id(src, rel, tgt),
        source_entity=src,
        relationship_type=rel,
        target_entity=tgt,
        source_knowledge_id=kid,
        source_version="v1",
        source_content_hash="h1",
        confidence="EXTRACTED",
    )


def test_in_memory_store_crud():
    store = InMemoryGraphStore()
    a = _sample_entity()
    b = _sample_entity("knowledge-service", "document", "k1")
    store.upsert_entity(a)
    store.upsert_entity(b)
    assert store.get_entity(a.entity_id) == a
    assert len(store.list_entities()) == 2
    assert store.find_entities_by_name("MEMORY-SERVICE") == [a]

    rel = _sample_relationship(a.entity_id, "references", b.entity_id)
    store.upsert_relationship(rel)
    assert store.get_relationship(rel.relationship_id) == rel
    assert a.entity_id in store.neighbors(b.entity_id)
    assert b.entity_id in store.neighbors(a.entity_id)


def test_in_memory_store_delete_by_knowledge():
    store = InMemoryGraphStore()
    a = _sample_entity(kid="k1")
    b = _sample_entity("other", "document", "k2")
    store.upsert_entity(a)
    store.upsert_entity(b)
    store.upsert_relationship(_sample_relationship(a.entity_id, "references", b.entity_id, "k1"))
    store.delete_by_knowledge("k1")
    assert store.get_entity(a.entity_id) is None
    assert store.get_entity(b.entity_id) is not None
    assert store.list_relationships() == []


def test_sqlite_store_round_trip():
    with tempfile.TemporaryDirectory() as tmp:
        store = SQLiteGraphStore(f"{tmp}/graph.sqlite3")
        a = _sample_entity()
        b = _sample_entity("knowledge-service", "document", "k1")
        store.upsert_entity(a)
        store.upsert_entity(b)
        rel = _sample_relationship(a.entity_id, "references", b.entity_id)
        store.upsert_relationship(rel)
        assert store.get_entity(a.entity_id).canonical_name == "memory-service"
        assert store.get_relationship(rel.relationship_id).relationship_type == "references"
        assert store.neighbors(b.entity_id) == [a.entity_id]
        check = store.consistency_check()
        assert check["entities"] == 2
        assert check["relationships"] == 1
        store.close()


def test_sqlite_store_upsert_is_idempotent():
    with tempfile.TemporaryDirectory() as tmp:
        store = SQLiteGraphStore(f"{tmp}/g.sqlite3")
        a = _sample_entity()
        store.upsert_entity(a)
        store.upsert_entity(a)  # same id -> overwrite
        assert len(store.list_entities()) == 1
        store.close()
