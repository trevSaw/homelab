"""Public service for knowledge ingestion.

The service is an internal Python component – it does **not** expose HTTP
endpoints.  It reads a local file, creates a :class:`KnowledgeDocument`, stores it
via a provided :class:`KnowledgeStore` and publishes a ``knowledge.ingestion.file``
event on the shared KORA ``EventBus``.
"""

from __future__ import annotations

import asyncio
from typing import Any

from ..storage.interface import KnowledgeStore
from ..ingestion.processor import process_ingestion
from app.event_bus import EventBus, EventEnvelope


class KnowledgeIngestionService:
    def __init__(self, store: KnowledgeStore, event_bus: EventBus) -> None:
        self._store = store
        self._bus = event_bus
        self._lock = asyncio.Lock()

    async def ingest(self, file_path: str) -> None:
        """Ingest a local file into the Knowledge store.

        1. Process the file into a :class:`KnowledgeDocument`.
        2. Save the document via the configured ``KnowledgeStore``.
        3. Publish a ``knowledge.ingestion.file`` event for any downstream
           observers.
        """
        async with self._lock:
            doc = process_ingestion(file_path)
            await self._store.save(doc)
            envelope = EventEnvelope(
                event_type="knowledge.ingestion.file",
                source="knowledge-ingestion-service",
                payload={"doc_id": doc.doc_id, "source": doc.source},
                metadata={"size": doc.metadata.get("size")},
            )
            self._bus.publish(envelope)
