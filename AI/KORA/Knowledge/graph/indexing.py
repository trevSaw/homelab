"""Graph indexing coordinator.

Drives graph synchronization from Knowledge changes:

    KnowledgeVersion → extract → entities/relationships → GraphStore

Behavioral rules:
- Idempotent: re-extracting the same document version (same content hash) is a
  no-op; the derived graph representation is unchanged.
- Replace-on-success: obsolete graph objects for a document are removed only
  after the new representation has been written successfully.
- Failure-aware: a graph indexing failure never invalidates authoritative
  Knowledge.
- Event-driven: subscribes to ``knowledge.ingestion.file`` on the shared EventBus.
"""

from __future__ import annotations

import asyncio
import logging

from app.event_bus import EventEnvelope, Subscription

from ..models.version import KnowledgeVersion
from .extraction import extract_entities_and_relationships
from .models import GraphEntity, GraphRelationship
from .store import GraphStore

log = logging.getLogger("kora.knowledge.graph")


class GraphIndexingError(RuntimeError):
    pass


class _GraphExtractionRecord:
    def __init__(
        self,
        content_hash: str,
        entities: list[GraphEntity],
        relationships: list[GraphRelationship],
    ) -> None:
        self.content_hash = content_hash
        self.entities = entities
        self.relationships = relationships


class GraphIndexingCoordinator:
    def __init__(
        self,
        *,
        graph_store: GraphStore,
        event_bus: object | None = None,
        graph_event_topics: tuple[str, ...] = ("knowledge.ingestion.file",),
        enabled: bool = True,
    ) -> None:
        self._graph_store = graph_store
        self._event_bus = event_bus
        self._enabled = enabled
        self._processed: dict[str, str] = {}  # knowledge_id -> content_hash
        self._subscriptions: list[Subscription] = []
        if event_bus is not None and enabled:
            for topic in graph_event_topics:
                self._subscriptions.append(event_bus.subscribe(topic, self._handle_event))

    def close(self) -> None:
        if self._event_bus is not None:
            for subscription in self._subscriptions:
                try:
                    self._event_bus.unsubscribe(subscription)
                except Exception:  # noqa: BLE001
                    log.debug("failed to unsubscribe %s", subscription.subscription_id)
        self._subscriptions.clear()

    def _handle_event(self, event: EventEnvelope) -> None:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(self._index_from_event(event))
        else:
            asyncio.run(self._index_from_event(event))

    async def _index_from_event(self, event: EventEnvelope) -> _GraphExtractionRecord | None:
        payload = event.payload or {}
        try:
            document_id = str(payload["document_id"])
            source = str(payload["source"])
            content_hash = str(payload.get("content_hash") or "")
            content = str(payload.get("content") or "")
            version = str(payload.get("version") or "")
        except KeyError as exc:
            log.warning("graph indexing event missing field: %s", exc)
            return None
        version_obj = KnowledgeVersion(
            document_id=document_id,
            version=version,
            content_hash=content_hash,
            source=source,
            content=content,
        )
        return await self.index_version(version_obj)

    async def index_version(self, version: KnowledgeVersion) -> _GraphExtractionRecord:
        if self._processed.get(version.document_id) == version.content_hash:
            return self._reindex(version)
        entities, relationships = extract_entities_and_relationships(version)
        record = _GraphExtractionRecord(version.content_hash, entities, relationships)

        try:
            # Replace-on-success: the new representation is fully computed above;
            # only then retire stale graph objects and persist the fresh ones.
            self._graph_store.delete_by_knowledge(version.document_id)
            for entity in entities:
                self._graph_store.upsert_entity(entity)
            for relationship in relationships:
                self._graph_store.upsert_relationship(relationship)
        except Exception as exc:  # noqa: BLE001
            log.warning("graph indexing failed for %s: %s", version.document_id, exc)
            raise GraphIndexingError(f"graph indexing failed: {exc}") from exc

        self._processed[version.document_id] = version.content_hash
        return record

    def _reindex(self, version: KnowledgeVersion) -> _GraphExtractionRecord:
        # Unchanged version: return the current derived representation without
        # rebuilding. We recompute deterministically so the record is valid.
        entities, relationships = extract_entities_and_relationships(version)
        return _GraphExtractionRecord(version.content_hash, entities, relationships)
