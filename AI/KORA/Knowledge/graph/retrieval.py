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
            matches = resolve_entities(self._graph_store, name)
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


# High-frequency tokens that should not anchor an entity match. Note: these are
# used ONLY for single-token partial matching — they never discard a whole
# canonical name. An entity whose name is entirely stopwords (e.g. "Memory")
# is still resolvable via exact / multi-token matching.
_SINGLE_TOKEN_STOPWORDS = frozenset({
    "what", "is", "are", "the", "a", "an", "how", "does", "do", "which",
    "where", "when", "who", "why", "can", "and", "or", "of", "to", "in",
    "for", "with", "about", "between", "relationship", "relate", "related",
    "relation", "connection", "connect", "connected", "link", "linked",
    "dependency", "depends", "graph", "please", "tell", "me", "explain",
})


def resolve_entities(graph_store: GraphStore, query: str) -> list[GraphEntity]:
    """Deterministically resolve graph entities for a natural-language query.

    Match priority:
      1. exact canonical-name match
      2. exact alias match
      3. normalized multi-token / entity-name match (entity's full name appears
         in the query, or the query's content tokens all appear in the entity)
      4. single-token partial match, only when it selects exactly one entity
         (unambiguous); otherwise no match
      5. otherwise no match

    Stopwords never discard an entity name: matching operates on the full
    canonical name token set, and single-token partial matching only falls back
    to non-stopword tokens.
    """
    # 1 & 2. exact canonical-name / alias match.
    exact = graph_store.find_entities_by_name(query)
    if exact:
        return exact

    entities = graph_store.list_entities()
    if not entities:
        return []

    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    # 3. normalized multi-token match.
    #
    # 3a. Entity whose full canonical name token set is contained in the query
    #     (i.e. the entity is "mentioned" in the query). This is the primary
    #     natural-language path and is safe against stopword discarding.
    mentioned: list[GraphEntity] = []
    for entity in entities:
        name_tokens = _tokenize(entity.canonical_name)
        if not name_tokens:
            continue
        if name_tokens <= query_tokens:
            mentioned.append(entity)
    if mentioned:
        return _sort_entities(mentioned)

    # 3b. Query content tokens all appear within a single entity's name. Only
    #     return when that match is unambiguous (exactly one entity).
    content_tokens = query_tokens - _SINGLE_TOKEN_STOPWORDS
    if content_tokens:
        covered: list[GraphEntity] = []
        for entity in entities:
            name_tokens = _tokenize(entity.canonical_name)
            if name_tokens and content_tokens <= name_tokens:
                covered.append(entity)
        if len(covered) == 1:
            return covered

    # 4. single-token partial match, only when unambiguous.
    for token in sorted(content_tokens, key=lambda t: len(t), reverse=True):
        matches = [
            entity
            for entity in entities
            if token in _tokenize(entity.canonical_name)
            or any(token in _tokenize(alias) for alias in entity.aliases)
        ]
        if len(matches) == 1:
            return matches
        if matches:
            # Ambiguous: do not guess.
            return []

    return []


def _tokenize(value: str) -> set[str]:
    """Lowercase alphanumeric token set; strips punctuation and whitespace."""
    import re

    return set(re.findall(r"[a-z0-9]+", value.lower()))


def _sort_entities(entities: list[GraphEntity]) -> list[GraphEntity]:
    return sorted(entities, key=lambda e: (len(_tokenize(e.canonical_name)), e.canonical_name))


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
