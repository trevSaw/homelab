"""Tests for deterministic entity/relationship extraction."""

from ..graph.extraction import extract_entities_and_relationships
from ..models.version import KnowledgeVersion


def _version(content: str, source: str = "/docs/architecture.md", doc_id: str = "k1", content_hash: str = "h1"):
    return KnowledgeVersion(
        document_id=doc_id,
        version="v1",
        content_hash=content_hash,
        source=source,
        content=content,
    )


def test_extracts_document_and_heading_entities():
    version = _version("# Architecture\n\n## Memory Service\n")
    entities, relationships = extract_entities_and_relationships(version)
    types = {e.entity_type for e in entities}
    assert "document" in types
    assert "heading" in types
    # file --contains--> heading
    assert any(
        r.relationship_type == "contains" and r.source_entity != r.target_entity
        for r in relationships
    )


def test_extracts_references_from_inline_and_wikilinks():
    version = _version(
        "See [Memory](./memory.md) and [[knowledge-service]] for details."
    )
    entities, relationships = extract_entities_and_relationships(version)
    refs = [r for r in relationships if r.relationship_type == "references"]
    assert refs, "expected references relationships"
    assert all(r.confidence == "EXTRACTED" for r in refs)
    # Every relationship is provenance-tagged.
    assert all(r.source_knowledge_id == "k1" for r in relationships)


def test_extracts_parent_child_heading_contains():
    version = _version("# A\n## A.1\n## A.2\n")
    entities, relationships = extract_entities_and_relationships(version)
    contains = [
        (r.source_entity, r.target_entity)
        for r in relationships
        if r.relationship_type == "contains"
    ]
    assert len(contains) >= 3  # file->A, A->A.1, A->A.2


def test_duplicate_extraction_is_deterministic():
    version = _version("# B\n\nreference [x](./x.md) and [[y]] here.")
    e1, r1 = extract_entities_and_relationships(version)
    e2, r2 = extract_entities_and_relationships(version)
    assert [e.entity_id for e in e1] == [e.entity_id for e in e2]
    assert [r.relationship_id for r in r1] == [r.relationship_id for r in r2]


def test_external_links_not_extracted_as_doc_refs():
    version = _version("See https://example.com and [mailto](mailto:x@y.z) and [img](./img.png).")
    _, relationships = extract_entities_and_relationships(version)
    refs = [r for r in relationships if r.relationship_type == "references"]
    assert refs == []


def test_empty_content_yields_document_only():
    version = _version("")
    entities, relationships = extract_entities_and_relationships(version)
    assert len(entities) == 1
    assert entities[0].entity_type == "document"
    assert relationships == []
