"""Deterministic entity/relationship extraction from Knowledge.

Mirrors Graphify's markdown extractor conventions so the derived graph is
compatible with Graphify's serve layer:

- one entity per document (type ``document``)
- one entity per markdown heading (``#``/``##``/``###``)
- ``contains`` relationships for heading hierarchy and file→heading
- ``references`` relationships for inline links, reference-style links, and
  ``[[wikilinks]]`` (EXTRACTED, matching Graphify)

Extraction is deterministic (no LLM), preserves provenance to the source
Knowledge document/version, and is idempotent.
"""

from __future__ import annotations

import re
from typing import Iterable

from ..models.version import KnowledgeVersion
from .models import (
    GraphEntity,
    GraphRelationship,
    entity_id,
    relationship_id,
)

_HEADING_RE = re.compile(r"^(#{1,3})\s+(.+?)\s*$")
_INLINE_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)#\s]+?)(?:#[^)]*)?\)")
_WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]")
_REF_LINK_DEF_RE = re.compile(r"^\[([^\]]+)\]:\s+([^#\s]+?)(?:#[^)]*)?\s*$")

_DOC_EXTENSIONS = {".md", ".mdx", ".qmd", ".markdown", ".rst", ".txt"}


def _entity_type_for_ref(target: str) -> str:
    lower = target.lower()
    for ext in _DOC_EXTENSIONS:
        if lower.endswith(ext):
            return "document"
    return "document"


def _strip_fragment(target: str) -> str:
    return target.split("#", 1)[0].split("?", 1)[0]


def _resolve_link(target: str) -> str | None:
    """Resolve a markdown link target; returns None for external/unsupported."""
    stripped = _strip_fragment(target).strip()
    if not stripped:
        return None
    if stripped.startswith(("http://", "https://", "mailto:", "//", "#")):
        return None
    lower = stripped.lower()
    if not any(lower.endswith(ext) for ext in _DOC_EXTENSIONS):
        return None
    return stripped


def extract_entities_and_relationships(
    version: KnowledgeVersion,
) -> tuple[list[GraphEntity], list[GraphRelationship]]:
    """Extract graph entities and relationships from a Knowledge version.

    Returns ``(entities, relationships)`` with provenance to ``version``.
    """
    content = version.content or ""
    source = version.source
    doc_name = source.rsplit("/", 1)[-1] or "document"

    doc_label = doc_name
    doc_entity = GraphEntity(
        entity_id=entity_id(doc_label, "document"),
        entity_type="document",
        canonical_name=doc_label,
        aliases=(doc_label.lower(),),
        source_knowledge_id=version.document_id,
        source_version=version.version,
        source_content_hash=version.content_hash,
        source_ref=source,
        metadata={"source_file": source, "source_location": "L1"},
    )

    entities: list[GraphEntity] = [doc_entity]
    relationships: list[GraphRelationship] = []
    seen_relationships: set[str] = set()
    heading_stack: list[tuple[int, GraphEntity]] = []

    lines = content.splitlines()

    for index, line in enumerate(lines, start=1):
        heading_match = _HEADING_RE.match(line)
        if heading_match:
            level = len(heading_match.group(1))
            heading_text = heading_match.group(2).strip()
            heading_entity = GraphEntity(
                entity_id=entity_id(heading_text, "heading"),
                entity_type="heading",
                canonical_name=heading_text,
                aliases=(heading_text.lower(),),
                source_knowledge_id=version.document_id,
                source_version=version.version,
                source_content_hash=version.content_hash,
                source_ref=source,
                metadata={"source_file": source, "source_location": f"L{index}"},
            )
            entities.append(heading_entity)

            # file --contains--> heading
            _add_relationship(
                relationships,
                seen_relationships,
                doc_entity.entity_id,
                "contains",
                heading_entity.entity_id,
                version,
                source,
                f"L{index}",
            )

            # parent heading --contains--> child heading (by nesting level)
            while heading_stack and heading_stack[-1][0] >= level:
                heading_stack.pop()
            if heading_stack:
                parent = heading_stack[-1][1]
                _add_relationship(
                    relationships,
                    seen_relationships,
                    parent.entity_id,
                    "contains",
                    heading_entity.entity_id,
                    version,
                    source,
                    f"L{index}",
                )
            heading_stack.append((level, heading_entity))
            continue

        ref_link_match = _REF_LINK_DEF_RE.match(line)
        if ref_link_match:
            target = _resolve_link(ref_link_match.group(2))
            if target:
                _add_relationship(
                    relationships,
                    seen_relationships,
                    doc_entity.entity_id,
                    "references",
                    entity_id(_target_label(target), _entity_type_for_ref(target)),
                    version,
                    source,
                    f"L{index}",
                )
            continue

        for match in _INLINE_LINK_RE.finditer(line):
            target = _resolve_link(match.group(1))
            if target:
                _add_relationship(
                    relationships,
                    seen_relationships,
                    doc_entity.entity_id,
                    "references",
                    entity_id(_target_label(target), _entity_type_for_ref(target)),
                    version,
                    source,
                    f"L{index}",
                )

        for match in _WIKILINK_RE.finditer(line):
            target = _resolve_link(match.group(1))
            if target:
                _add_relationship(
                    relationships,
                    seen_relationships,
                    doc_entity.entity_id,
                    "references",
                    entity_id(_target_label(target), _entity_type_for_ref(target)),
                    version,
                    source,
                    f"L{index}",
                )

    return entities, relationships


def _target_label(target: str) -> str:
    stripped = _strip_fragment(target).strip()
    base = stripped.rsplit("/", 1)[-1]
    for ext in _DOC_EXTENSIONS:
        if base.lower().endswith(ext):
            return base[: -len(ext)]
    return base


def _add_relationship(
    relationships: list[GraphRelationship],
    seen: set[str],
    source_entity: str,
    rel_type: str,
    target_entity: str,
    version: KnowledgeVersion,
    source_ref: str,
    location: str,
) -> None:
    rid = relationship_id(source_entity, rel_type, target_entity)
    if rid in seen:
        return
    seen.add(rid)
    relationships.append(
        GraphRelationship(
            relationship_id=rid,
            source_entity=source_entity,
            relationship_type=rel_type,
            target_entity=target_entity,
            source_knowledge_id=version.document_id,
            source_version=version.version,
            source_content_hash=version.content_hash,
            source_ref=source_ref,
            confidence="EXTRACTED",
            metadata={"source_location": location},
        )
    )
