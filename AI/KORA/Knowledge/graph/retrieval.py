"""KORA-owned graph retrieval.

The Runtime depends on this abstraction, not directly on Graphify. Graph
retrieval returns entities/relationships with provenance back to authoritative
Knowledge. Graph failures degrade safely.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from .models import GraphEntity, GraphRelationship
from .store import GraphStore

log = logging.getLogger("kora.knowledge.graph.retrieval")


class GraphRetrievalBackendError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class GraphEntityResult:
    entity_id: str
    entity_type: str
    canonical_name: str
    source_knowledge_id: str
    source_version: str
    source_ref: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "canonical_name": self.canonical_name,
            "source_knowledge_id": self.source_knowledge_id,
            "source_version": self.source_version,
            "source_ref": self.source_ref,
        }


@dataclass(frozen=True, slots=True)
class GraphRelationshipResult:
    relationship_id: str
    source_entity: str
    relationship_type: str
    target_entity: str
    source_knowledge_id: str
    confidence: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "relationship_id": self.relationship_id,
            "source_entity": self.source_entity,
            "relationship_type": self.relationship_type,
            "target_entity": self.target_entity,
            "source_knowledge_id": self.source_knowledge_id,
            "confidence": self.confidence,
        }


@dataclass(frozen=True, slots=True)
class GraphRetrievalResult:
    query: str
    status: str  # "ok" | "degraded"
    backend: str
    entities: tuple[GraphEntityResult, ...]
    relationships: tuple[GraphRelationshipResult, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "status": self.status,
            "backend": self.backend,
            "entities": [e.to_dict() for e in self.entities],
            "relationships": [r.to_dict() for r in self.relationships],
        }


class GraphRetrievalService:
    def __init__(
        self,
        *,
        graph_store: GraphStore,
        backend_name: str = "local_graph",
    ) -> None:
        self._graph_store = graph_store
        self._backend_name = backend_name

    @property
    def backend_name(self) -> str:
        return self._backend_name

    async def lookup_entity(self, name: str) -> GraphRetrievalResult:
        try:
            matches = self._graph_store.find_entities_by_name(name)
        except Exception as exc:  # noqa: BLE001
            log.warning("graph entity lookup degraded: %s", exc)
            return GraphRetrievalResult(name, "degraded", self._backend_name, (), ())
        entities = tuple(_to_entity_result(e) for e in matches)
        relationships: tuple[GraphRelationshipResult, ...] = ()
        if entities:
            seen: set[str] = set()
            collected: list[GraphRelationship] = []
            for e in matches:
                for r in self._graph_store.relationships_for_entity(e.entity_id):
                    if r.relationship_id not in seen:
                        seen.add(r.relationship_id)
                        collected.append(r)
            relationships = tuple(_to_relationship_result(r) for r in collected)
        return GraphRetrievalResult(name, "ok", self._backend_name, entities, relationships)

    async def neighbors(self, entity_id: str) -> GraphRetrievalResult:
        try:
            entities: list[GraphEntity] = []
            entity = self._graph_store.get_entity(entity_id)
            if entity is not None:
                entities.append(entity)
            neighbor_ids = self._graph_store.neighbors(entity_id)
            relationships: list[GraphRelationship] = []
            for rid in neighbor_ids:
                neighbor = self._graph_store.get_entity(rid)
                if neighbor is not None:
                    entities.append(neighbor)
                relationships.extend(self._graph_store.relationships_for_entity(rid))
        except Exception as exc:  # noqa: BLE001
            log.warning("graph neighbor retrieval degraded: %s", exc)
            return GraphRetrievalResult(entity_id, "degraded", self._backend_name, (), ())
        return GraphRetrievalResult(
            entity_id,
            "ok",
            self._backend_name,
            tuple(_to_entity_result(e) for e in entities),
            tuple(_to_relationship_result(r) for r in relationships),
        )

    async def relationships(self, entity_id: str) -> GraphRetrievalResult:
        try:
            entity = self._graph_store.get_entity(entity_id)
            rels = self._graph_store.relationships_for_entity(entity_id)
        except Exception as exc:  # noqa: BLE001
            log.warning("graph relationship retrieval degraded: %s", exc)
            return GraphRetrievalResult(entity_id, "degraded", self._backend_name, (), ())
        entities = (tuple(_to_entity_result(entity)) if entity else ())
        return GraphRetrievalResult(
            entity_id,
            "ok",
            self._backend_name,
            entities,
            tuple(_to_relationship_result(r) for r in rels),
        )

    async def health(self) -> bool:
        try:
            self._graph_store.list_entities()
            return True
        except Exception:  # noqa: BLE001
            return False


def _to_entity_result(entity: GraphEntity) -> GraphEntityResult:
    return GraphEntityResult(
        entity_id=entity.entity_id,
        entity_type=entity.entity_type,
        canonical_name=entity.canonical_name,
        source_knowledge_id=entity.source_knowledge_id,
        source_version=entity.source_version,
        source_ref=entity.source_ref,
    )


def _to_relationship_result(rel: GraphRelationship) -> GraphRelationshipResult:
    return GraphRelationshipResult(
        relationship_id=rel.relationship_id,
        source_entity=rel.source_entity,
        relationship_type=rel.relationship_type,
        target_entity=rel.target_entity,
        source_knowledge_id=rel.source_knowledge_id,
        confidence=rel.confidence,
    )
