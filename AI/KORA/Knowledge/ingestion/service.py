"""Public service for knowledge ingestion.

The service is an internal Python component – it does **not** expose HTTP
endpoints. It reads a local file, creates a :class:`KnowledgeDocument`, stores it
via a provided :class:`KnowledgeStore`, computes version identity, and publishes a
``knowledge.ingestion.file`` event carrying versioned metadata (including content)
so the indexing coordinator can chunk/embed/index without coupling to the store.
"""

from __future__ import annotations

import asyncio
from typing import Any

from app.event_bus import EventBus, EventEnvelope

from ..models.version import KnowledgeVersion
from ..storage.interface import KnowledgeStore
from .processor import process_ingestion


class KnowledgeIngestionService:
    def __init__(self, store: KnowledgeStore, event_bus: EventBus) -> None:
        self._store = store
        self._bus = event_bus
        self._lock = asyncio.Lock()

    async def ingest(self, file_path: str) -> KnowledgeVersion:
        """Ingest a local file into the Knowledge store and publish an indexing event.

        1. Process the file into a :class:`KnowledgeDocument`.
        2. Save the document via the configured ``KnowledgeStore``.
        3. Compute version identity.
        4. Publish a ``knowledge.ingestion.file`` event for downstream observers
           (e.g. the indexing coordinator).
        """
        async with self._lock:
            doc = process_ingestion(file_path)
            await self._store.save(doc)
            version = KnowledgeVersion.from_document(doc)
            envelope = EventEnvelope(
                event_type="knowledge.ingestion.file",
                source="knowledge-ingestion-service",
                payload={
                    "document_id": version.document_id,
                    "version": version.version,
                    "content_hash": version.content_hash,
                    "source": version.source,
                    "content": version.content,
                    "metadata": dict(version.metadata),
                },
                metadata={"size": doc.metadata.get("size")},
            )
            self._bus.publish(envelope)
            return version

    async def ingest_version(self, version: KnowledgeVersion) -> None:
        """Publish an indexing event for an already-built KnowledgeVersion."""
        async with self._lock:
            envelope = EventEnvelope(
                event_type="knowledge.ingestion.file",
                source="knowledge-ingestion-service",
                payload={
                    "document_id": version.document_id,
                    "version": version.version,
                    "content_hash": version.content_hash,
                    "source": version.source,
                    "content": version.content,
                    "metadata": dict(version.metadata),
                },
            )
            self._bus.publish(envelope)
