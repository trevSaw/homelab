"""Graph data model for Knowledge relationships.

Every graph object that originates from Knowledge retains provenance: source
Knowledge document id, version, content hash, and the extraction source. Graph
objects are a derived representation of authoritative Knowledge, never
authoritative themselves.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def entity_id(canonical_name: str, entity_type: str) -> str:
    """Deterministic entity identity from normalized name + type.

    Same canonical name + type always yields the same entity id, so re-indexing
    identical Knowledge does not create duplicate graph entities.
    """
    import hashlib

    raw = f"{entity_type}::{canonical_name.lower().strip()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def relationship_id(source_entity: str, rel_type: str, target_entity: str) -> str:
    import hashlib

    raw = f"{source_entity}::{rel_type}::{target_entity}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


@dataclass(frozen=True, slots=True)
class GraphEntity:
    entity_id: str
    entity_type: str
    canonical_name: str
    aliases: tuple[str, ...] = ()
    source_knowledge_id: str = ""
    source_version: str = ""
    source_content_hash: str = ""
    source_ref: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "canonical_name": self.canonical_name,
            "aliases": list(self.aliases),
            "source_knowledge_id": self.source_knowledge_id,
            "source_version": self.source_version,
            "source_content_hash": self.source_content_hash,
            "source_ref": self.source_ref,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }


@dataclass(frozen=True, slots=True)
class GraphRelationship:
    relationship_id: str
    source_entity: str
    relationship_type: str
    target_entity: str
    source_knowledge_id: str = ""
    source_version: str = ""
    source_content_hash: str = ""
    source_ref: str = ""
    confidence: str = "EXTRACTED"  # EXTRACTED | INFERRED (Graphify convention)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "relationship_id": self.relationship_id,
            "source_entity": self.source_entity,
            "relationship_type": self.relationship_type,
            "target_entity": self.target_entity,
            "source_knowledge_id": self.source_knowledge_id,
            "source_version": self.source_version,
            "source_content_hash": self.source_content_hash,
            "source_ref": self.source_ref,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }
