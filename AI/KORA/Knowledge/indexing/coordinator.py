"""Knowledge indexing coordinator.

Drives the pipeline:

    KnowledgeVersion → chunk → embed → index → metadata

Behavioral rules:
- Idempotent: re-indexing the same document version (same content hash) with the
  same embedding model is a no-op that returns the existing state.
- Replace-on-success: a new index is built before the old one is retired. If
  embedding or indexing fails, the previously usable index remains available.
- Failure-aware: a failed index records ``IndexState.FAILED`` metadata and never
  invalidates authoritative Knowledge.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from app.event_bus import EventEnvelope, Subscription

from ..chunking.interface import Chunker
from ..embedding.interface import EmbeddingError, EmbeddingProvider
from ..models.chunk import KnowledgeChunk
from ..models.index_state import IndexMetadata, IndexState
from ..models.version import KnowledgeVersion
from ..storage.index_metadata import IndexMetadataStore
from ..storage.vector import VectorStore, VectorStoreError

log = logging.getLogger("kora.knowledge.indexing")


class IndexingError(RuntimeError):
    pass


class IndexingCoordinator:
    def __init__(
        self,
        *,
        chunker: Chunker,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
        metadata_store: IndexMetadataStore,
        event_bus: Any | None = None,
        indexing_event_topics: tuple[str, ...] = ("knowledge.ingestion.file",),
        replace_on_success: bool = True,
    ) -> None:
        self._chunker = chunker
        self._embedding = embedding_provider
        self._vector_store = vector_store
        self._metadata_store = metadata_store
        self._replace_on_success = replace_on_success
        self._event_bus = event_bus
        self._subscriptions: list[Subscription] = []
        if event_bus is not None:
            for topic in indexing_event_topics:
                self._subscriptions.append(
                    event_bus.subscribe(topic, self._handle_event)
                )

    def close(self) -> None:
        if self._event_bus is not None:
            for subscription in self._subscriptions:
                try:
                    self._event_bus.unsubscribe(subscription)
                except Exception:  # noqa: BLE001
                    log.debug("failed to unsubscribe %s", subscription.subscription_id)
        self._subscriptions.clear()

    def _handle_event(self, event: EventEnvelope) -> None:
        """Synchronous EventBus handler that schedules async indexing."""
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(self._index_from_event(event))
        else:
            asyncio.run(self._index_from_event(event))

    async def _index_from_event(self, event: EventEnvelope) -> IndexMetadata | None:
        payload = event.payload or {}
        try:
            document_id = str(payload["document_id"])
            source = str(payload["source"])
            content_hash = str(payload.get("content_hash") or "")
            content = str(payload.get("content") or "")
            version = str(payload.get("version") or "")
            metadata = dict(payload.get("metadata") or {})
        except KeyError as exc:
            log.warning("knowledge indexing event missing field: %s", exc)
            return None
        version_obj = KnowledgeVersion(
            document_id=document_id,
            version=version,
            content_hash=content_hash,
            source=source,
            content=content,
            metadata=metadata,
        )
        return await self.index_version(version_obj)

    async def index_version(self, version: KnowledgeVersion) -> IndexMetadata:
        existing = self._metadata_store.get(version.document_id)
        if (
            existing is not None
            and existing.index_state == IndexState.INDEXED
            and existing.content_hash == version.content_hash
            and existing.embedding_model == self._embedding.model_id
        ):
            return existing

        chunks = self._chunk_version(version)
        if not chunks:
            return self._record(
                version, IndexState.INDEXED, chunk_ids=(), chunk_count=0, error=None
            )

        try:
            embeddings = await self._embedding.embed([chunk.content for chunk in chunks])
        except EmbeddingError as exc:
            return self._record(
                version, IndexState.FAILED, chunk_ids=(), chunk_count=0, error=str(exc)
            )

        if len(embeddings) != len(chunks):
            error = "embedding provider returned a mismatched number of vectors"
            return self._record(
                version, IndexState.FAILED, chunk_ids=(), chunk_count=0, error=error
            )

        ids = [chunk.chunk_id for chunk in chunks]
        documents = [chunk.content for chunk in chunks]
        metadatas = [
            {**chunk.to_metadata(), "embedding_model": self._embedding.model_id}
            for chunk in chunks
        ]

        try:
            await self._vector_store.upsert(ids, embeddings, documents, metadatas)
        except VectorStoreError as exc:
            return self._record(
                version, IndexState.FAILED, chunk_ids=(), chunk_count=0, error=str(exc)
            )

        if self._replace_on_success and existing is not None:
            stale = [cid for cid in existing.chunk_ids if cid not in set(ids)]
            if stale:
                try:
                    await self._vector_store.delete(stale)
                except VectorStoreError as exc:  # noqa: BLE001
                    log.warning("failed to retire stale chunks: %s", exc)

        return self._record(
            version, IndexState.INDEXED, chunk_ids=tuple(ids), chunk_count=len(ids), error=None
        )

    def _chunk_version(self, version: KnowledgeVersion) -> list[KnowledgeChunk]:
        pieces = self._chunker.chunk(version.content)
        return [
            KnowledgeChunk(
                document_id=version.document_id,
                version=version.version,
                content_hash=version.content_hash,
                source=version.source,
                index=i,
                content=piece,
                embedding_model=self._embedding.model_id,
            )
            for i, piece in enumerate(pieces)
        ]

    def _record(
        self,
        version: KnowledgeVersion,
        state: str,
        *,
        chunk_ids: tuple[str, ...],
        chunk_count: int,
        error: str | None,
    ) -> IndexMetadata:
        metadata = IndexMetadata(
            document_id=version.document_id,
            version=version.version,
            content_hash=version.content_hash,
            index_state=state,
            embedding_model=self._embedding.model_id,
            source=version.source,
            chunk_ids=chunk_ids,
            chunk_count=chunk_count,
            last_error=error,
        )
        self._metadata_store.upsert(metadata)
        return metadata
