"""Knowledge Service facade.

Owns the Knowledge lifecycle boundary (Phase 14.3). Composes ingestion, indexing,
and retrieval behind a single KORA-owned service. The Runtime depends on this
facade, not on Chroma or embedding implementations directly.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

from app.event_bus import EventBus, EventEnvelope

from .config import KnowledgeConfig
from .context.assembly import KnowledgeContext, KnowledgeContextAssembler
from .embedding.interface import EmbeddingProvider
from .embedding.ollama import OllamaEmbeddingProvider
from .indexing.coordinator import IndexingCoordinator
from .ingestion.service import KnowledgeIngestionService
from .models.version import KnowledgeVersion
from .retrieval.service import KnowledgeRetrievalService
from .storage.chroma import ChromaVectorStore
from .storage.index_metadata import IndexMetadataStore, SQLiteIndexMetadataStore
from .storage.interface import KnowledgeStore
from .storage.in_memory_vector import InMemoryVectorStore
from .storage.vector import VectorStore
from .chunking.fixed_size import FixedSizeChunker


@dataclass(slots=True)
class KnowledgeService:
    config: KnowledgeConfig
    store: KnowledgeStore
    event_bus: EventBus
    embedding_provider: EmbeddingProvider
    vector_store: VectorStore
    index_metadata: IndexMetadataStore
    ingestion: KnowledgeIngestionService = field(init=False)
    indexing: IndexingCoordinator = field(init=False)
    retrieval: KnowledgeRetrievalService = field(init=False)
    assembler: KnowledgeContextAssembler = field(init=False)

    def __post_init__(self) -> None:
        self.ingestion = KnowledgeIngestionService(self.store, self.event_bus)
        chunker = FixedSizeChunker(
            size=self.config.chunk_size, overlap=self.config.chunk_overlap
        )
        self.indexing = IndexingCoordinator(
            chunker=chunker,
            embedding_provider=self.embedding_provider,
            vector_store=self.vector_store,
            metadata_store=self.index_metadata,
            event_bus=self.event_bus if self.config.indexing_enabled else None,
            indexing_event_topics=self.config.indexing_event_topics,
            replace_on_success=self.config.replace_on_success,
        )
        self.retrieval = KnowledgeRetrievalService(
            embedding_provider=self.embedding_provider,
            vector_store=self.vector_store,
            top_k=self.config.retrieval_top_k,
        )
        self.assembler = KnowledgeContextAssembler(
            retrieval_service=self.retrieval,
            top_k=self.config.retrieval_top_k,
        )

    async def ingest_file(self, file_path: str) -> KnowledgeVersion:
        return await self.ingestion.ingest(file_path)

    async def retrieve(self, query: str, *, top_k: int | None = None) -> Any:
        return await self.retrieval.retrieve(query, top_k=top_k)

    async def build_context(self, query: str, *, top_k: int | None = None) -> KnowledgeContext:
        return await self.assembler.build_context(query, top_k=top_k)

    async def index_version(self, version: KnowledgeVersion) -> Any:
        return await self.indexing.index_version(version)

    async def health(self) -> dict[str, Any]:
        vector_healthy = await self._safe_health()
        return {
            "status": "ok" if vector_healthy else "degraded",
            "embedding_model": self.embedding_provider.model_id,
            "vector_store": "chroma",
            "indexed_documents": len(self.index_metadata.list_indexed()),
            "vector_healthy": vector_healthy,
        }

    async def _safe_health(self) -> bool:
        try:
            return await self.vector_store.health()
        except Exception:  # noqa: BLE001
            return False

    async def close(self) -> None:
        self.indexing.close()
        await _aclose(self.embedding_provider)
        await _aclose(self.vector_store)
        self.index_metadata.close()


async def _aclose(obj: Any) -> None:
    close = getattr(obj, "close", None)
    if close is not None:
        result = close()
        if asyncio.iscoroutine(result):
            await result


def build_knowledge_service(
    *,
    config: KnowledgeConfig,
    store: KnowledgeStore,
    event_bus: EventBus,
    embedding_transport: Any | None = None,
    vector_transport: Any | None = None,
) -> KnowledgeService:
    """Composition boundary: builds providers behind the Knowledge abstraction."""
    embedding_provider = OllamaEmbeddingProvider(
        base_url=config.embedding_base_url,
        model=config.embedding_model,
        timeout_seconds=config.embedding_timeout_seconds,
        retry_attempts=config.embedding_retry_attempts,
        retry_base_seconds=config.embedding_retry_base_seconds,
        transport=embedding_transport,
    )
    if config.vector_provider == "in_memory":
        vector_store: VectorStore = InMemoryVectorStore()
    else:
        vector_store = ChromaVectorStore(
            base_url=config.chroma_base_url,
            collection=config.chroma_collection,
            timeout_seconds=config.chroma_timeout_seconds,
            retry_attempts=config.chroma_retry_attempts,
            transport=vector_transport,
        )
    if config.index_metadata_sqlite_enabled:
        from .storage.index_metadata import InMemoryIndexMetadataStore

        try:
            index_metadata: IndexMetadataStore = SQLiteIndexMetadataStore(
                config.index_metadata_db_path
            )
        except Exception:  # noqa: BLE001
            # Fall back to in-memory metadata when the DB path is not writable.
            index_metadata = InMemoryIndexMetadataStore()
    else:
        from .storage.index_metadata import InMemoryIndexMetadataStore

        index_metadata = InMemoryIndexMetadataStore()
    return KnowledgeService(
        config=config,
        store=store,
        event_bus=event_bus,
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        index_metadata=index_metadata,
    )
