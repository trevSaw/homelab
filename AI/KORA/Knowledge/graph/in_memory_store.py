"""In-memory GraphStore implementation used for tests and local fallback."""

from __future__ import annotations

import threading

from .models import GraphEntity, GraphRelationship


class InMemoryGraphStore:
    def __init__(self) -> None:
        self._entities: dict[str, GraphEntity] = {}
        self._relationships: dict[str, GraphRelationship] = {}
        self._lock = threading.RLock()

    def get_entity(self, entity_id: str) -> GraphEntity | None:
        with self._lock:
            return self._entities.get(entity_id)

    def upsert_entity(self, entity: GraphEntity) -> None:
        with self._lock:
            self._entities[entity.entity_id] = entity

    def list_entities(self) -> list[GraphEntity]:
        with self._lock:
            return sorted(self._entities.values(), key=lambda e: e.canonical_name)

    def find_entities_by_name(self, name: str) -> list[GraphEntity]:
        needle = _normalize(name)
        with self._lock:
            return [
                e
                for e in self._entities.values()
                if _normalize(e.canonical_name) == needle
                or any(_normalize(a) == needle for a in e.aliases)
            ]

    def get_relationship(self, relationship_id: str) -> GraphRelationship | None:
        with self._lock:
            return self._relationships.get(relationship_id)

    def upsert_relationship(self, relationship: GraphRelationship) -> None:
        with self._lock:
            self._relationships[relationship.relationship_id] = relationship

    def list_relationships(self) -> list[GraphRelationship]:
        with self._lock:
            return sorted(
                self._relationships.values(),
                key=lambda r: (r.source_entity, r.relationship_type, r.target_entity),
            )

    def relationships_for_entity(self, entity_id: str) -> list[GraphRelationship]:
        with self._lock:
            return [
                r
                for r in self._relationships.values()
                if r.source_entity == entity_id or r.target_entity == entity_id
            ]

    def neighbors(self, entity_id: str) -> list[str]:
        with self._lock:
            result: list[str] = []
            for r in self._relationships.values():
                if r.source_entity == entity_id:
                    result.append(r.target_entity)
                elif r.target_entity == entity_id:
                    result.append(r.source_entity)
            return sorted(set(result))

    def delete_by_knowledge(self, source_knowledge_id: str) -> None:
        with self._lock:
            for eid in [
                e.entity_id for e in self._entities.values()
                if e.source_knowledge_id == source_knowledge_id
            ]:
                self._entities.pop(eid, None)
            for rid in [
                r.relationship_id for r in self._relationships.values()
                if r.source_knowledge_id == source_knowledge_id
            ]:
                self._relationships.pop(rid, None)

    def close(self) -> None:
        pass


def _normalize(value: str) -> str:
    return "".join(ch for ch in value.lower().strip() if ch.isalnum())
