"""Phase 14.3 Knowledge Platform configuration.

The Knowledge Platform is configuration-driven. Values may come from
``knowledge_runtime.yaml`` (via ``from_dict``) with environment overrides applied
through ``from_env``/``resolve``. No environment-specific values are hard-coded.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class KnowledgeConfig:
    # Embedding
    embedding_provider: str = "ollama"
    embedding_model: str = "nomic-embed-text"
    embedding_base_url: str = "http://ollama:11434"
    embedding_timeout_seconds: float = 60.0
    embedding_retry_attempts: int = 2
    embedding_retry_base_seconds: float = 0.2

    # Vector store
    vector_provider: str = "chroma"
    chroma_base_url: str = "http://chromadb:8000"
    chroma_collection: str = "kora_knowledge"
    chroma_timeout_seconds: float = 30.0
    chroma_retry_attempts: int = 2

    # Chunking
    chunk_size: int = 512
    chunk_overlap: int = 64

    # Indexing
    indexing_enabled: bool = True
    replace_on_success: bool = True
    index_metadata_sqlite_enabled: bool = True
    index_metadata_db_path: str = "/data/knowledge-index.sqlite3"

    # Retrieval
    retrieval_enabled: bool = True
    retrieval_top_k: int = 5

    # Eventing
    indexing_event_topics: tuple[str, ...] = ("knowledge.ingestion.file",)

    # Graph (Phase 14.4)
    graph_enabled: bool = True
    graph_provider: str = "local"  # "local" | "graphify"
    graph_store_sqlite_enabled: bool = True
    graph_store_db_path: str = "/data/knowledge-graph.sqlite3"
    graphify_base_url: str = "http://graphify:8080"
    graphify_api_key: str = ""
    graphify_timeout_seconds: float = 30.0
    graphify_retry_attempts: int = 2
    graph_export_path: str = "/data/graph.json"
    graph_event_topics: tuple[str, ...] = ("knowledge.ingestion.file",)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "KnowledgeConfig":
        embedding = value.get("embedding") or {}
        vector = value.get("vector") or {}
        chunking = value.get("chunking") or {}
        indexing = value.get("indexing") or {}
        retrieval = value.get("retrieval") or {}
        events = value.get("events") or {}
        graph = value.get("graph") or {}
        return cls(
            embedding_provider=str(embedding.get("provider", "ollama")),
            embedding_model=str(embedding.get("model", "nomic-embed-text")),
            embedding_base_url=str(embedding.get("base_url", "http://ollama:11434")),
            embedding_timeout_seconds=float(embedding.get("timeout_seconds", 60.0)),
            embedding_retry_attempts=int(embedding.get("retry_attempts", 2)),
            embedding_retry_base_seconds=float(embedding.get("retry_base_seconds", 0.2)),
            vector_provider=str(vector.get("provider", "chroma")),
            chroma_base_url=str(vector.get("base_url", "http://chromadb:8000")),
            chroma_collection=str(vector.get("collection", "kora_knowledge")),
            chroma_timeout_seconds=float(vector.get("timeout_seconds", 30.0)),
            chroma_retry_attempts=int(vector.get("retry_attempts", 2)),
            chunk_size=int(chunking.get("size", 512)),
            chunk_overlap=int(chunking.get("overlap", 64)),
            indexing_enabled=bool(indexing.get("enabled", True)),
            replace_on_success=bool(indexing.get("replace_on_success", True)),
            index_metadata_sqlite_enabled=bool(
                indexing.get("metadata_sqlite_enabled", True)
            ),
            index_metadata_db_path=str(
                indexing.get("metadata_db_path", "/data/knowledge-index.sqlite3")
            ),
            retrieval_enabled=bool(retrieval.get("enabled", True)),
            retrieval_top_k=int(retrieval.get("top_k", 5)),
            indexing_event_topics=tuple(
                events.get("indexing_topics")
                or ("knowledge.ingestion.file",)
            ),
            graph_enabled=bool(graph.get("enabled", True)),
            graph_provider=str(graph.get("provider", "local")),
            graph_store_sqlite_enabled=bool(graph.get("store_sqlite_enabled", True)),
            graph_store_db_path=str(
                graph.get("store_db_path", "/data/knowledge-graph.sqlite3")
            ),
            graphify_base_url=str(graph.get("graphify_base_url", "http://graphify:8080")),
            graphify_api_key=str(graph.get("graphify_api_key", "")),
            graphify_timeout_seconds=float(graph.get("graphify_timeout_seconds", 30.0)),
            graphify_retry_attempts=int(graph.get("graphify_retry_attempts", 2)),
            graph_export_path=str(graph.get("export_path", "/data/graph.json")),
            graph_event_topics=tuple(
                graph.get("event_topics") or ("knowledge.ingestion.file",)
            ),
        )

    @classmethod
    def from_env(cls) -> "KnowledgeConfig":
        """Apply environment overrides on top of defaults."""
        cfg = cls()
        return cls(
            embedding_provider=os.environ.get("KORA_EMBEDDING_PROVIDER", cfg.embedding_provider),
            embedding_model=os.environ.get("KORA_EMBEDDING_MODEL", cfg.embedding_model),
            embedding_base_url=os.environ.get("KORA_EMBEDDING_BASE_URL", cfg.embedding_base_url),
            embedding_timeout_seconds=float(
                os.environ.get("KORA_EMBEDDING_TIMEOUT_SECONDS", cfg.embedding_timeout_seconds)
            ),
            embedding_retry_attempts=int(
                os.environ.get("KORA_EMBEDDING_RETRY_ATTEMPTS", cfg.embedding_retry_attempts)
            ),
            embedding_retry_base_seconds=float(
                os.environ.get(
                    "KORA_EMBEDDING_RETRY_BASE_SECONDS", cfg.embedding_retry_base_seconds
                )
            ),
            vector_provider=os.environ.get("KORA_VECTOR_PROVIDER", cfg.vector_provider),
            chroma_base_url=os.environ.get("KORA_CHROMA_BASE_URL", cfg.chroma_base_url),
            chroma_collection=os.environ.get("KORA_CHROMA_COLLECTION", cfg.chroma_collection),
            chroma_timeout_seconds=float(
                os.environ.get("KORA_CHROMA_TIMEOUT_SECONDS", cfg.chroma_timeout_seconds)
            ),
            chroma_retry_attempts=int(
                os.environ.get("KORA_CHROMA_RETRY_ATTEMPTS", cfg.chroma_retry_attempts)
            ),
            chunk_size=int(os.environ.get("KORA_CHUNK_SIZE", cfg.chunk_size)),
            chunk_overlap=int(os.environ.get("KORA_CHUNK_OVERLAP", cfg.chunk_overlap)),
            indexing_enabled=_env_bool("KORA_INDEXING_ENABLED", cfg.indexing_enabled),
            replace_on_success=_env_bool("KORA_INDEXING_REPLACE_ON_SUCCESS", cfg.replace_on_success),
            index_metadata_sqlite_enabled=_env_bool(
                "KORA_INDEX_METADATA_SQLITE", cfg.index_metadata_sqlite_enabled
            ),
            index_metadata_db_path=os.environ.get(
                "KORA_INDEX_METADATA_DB_PATH", cfg.index_metadata_db_path
            ),
            retrieval_enabled=_env_bool("KORA_RETRIEVAL_ENABLED", cfg.retrieval_enabled),
            retrieval_top_k=int(os.environ.get("KORA_RETRIEVAL_TOP_K", cfg.retrieval_top_k)),
            indexing_event_topics=cfg.indexing_event_topics,
            graph_enabled=_env_bool("KORA_GRAPH_ENABLED", cfg.graph_enabled),
            graph_provider=os.environ.get("KORA_GRAPH_PROVIDER", cfg.graph_provider),
            graph_store_sqlite_enabled=_env_bool(
                "KORA_GRAPH_STORE_SQLITE", cfg.graph_store_sqlite_enabled
            ),
            graph_store_db_path=os.environ.get(
                "KORA_GRAPH_STORE_DB_PATH", cfg.graph_store_db_path
            ),
            graphify_base_url=os.environ.get("KORA_GRAPHIFY_BASE_URL", cfg.graphify_base_url),
            graphify_api_key=os.environ.get("KORA_GRAPHIFY_API_KEY", cfg.graphify_api_key),
            graphify_timeout_seconds=float(
                os.environ.get("KORA_GRAPHIFY_TIMEOUT_SECONDS", cfg.graphify_timeout_seconds)
            ),
            graphify_retry_attempts=int(
                os.environ.get("KORA_GRAPHIFY_RETRY_ATTEMPTS", cfg.graphify_retry_attempts)
            ),
            graph_export_path=os.environ.get("KORA_GRAPH_EXPORT_PATH", cfg.graph_export_path),
            graph_event_topics=cfg.graph_event_topics,
        )


    def with_env_overrides(self) -> "KnowledgeConfig":
        """Return a copy of this config with environment variables overlaid."""
        return KnowledgeConfig(
            embedding_provider=os.environ.get("KORA_EMBEDDING_PROVIDER", self.embedding_provider),
            embedding_model=os.environ.get("KORA_EMBEDDING_MODEL", self.embedding_model),
            embedding_base_url=os.environ.get("KORA_EMBEDDING_BASE_URL", self.embedding_base_url),
            embedding_timeout_seconds=float(
                os.environ.get("KORA_EMBEDDING_TIMEOUT_SECONDS", self.embedding_timeout_seconds)
            ),
            embedding_retry_attempts=int(
                os.environ.get("KORA_EMBEDDING_RETRY_ATTEMPTS", self.embedding_retry_attempts)
            ),
            embedding_retry_base_seconds=float(
                os.environ.get("KORA_EMBEDDING_RETRY_BASE_SECONDS", self.embedding_retry_base_seconds)
            ),
            vector_provider=os.environ.get("KORA_VECTOR_PROVIDER", self.vector_provider),
            chroma_base_url=os.environ.get("KORA_CHROMA_BASE_URL", self.chroma_base_url),
            chroma_collection=os.environ.get("KORA_CHROMA_COLLECTION", self.chroma_collection),
            chroma_timeout_seconds=float(
                os.environ.get("KORA_CHROMA_TIMEOUT_SECONDS", self.chroma_timeout_seconds)
            ),
            chroma_retry_attempts=int(
                os.environ.get("KORA_CHROMA_RETRY_ATTEMPTS", self.chroma_retry_attempts)
            ),
            chunk_size=int(os.environ.get("KORA_CHUNK_SIZE", self.chunk_size)),
            chunk_overlap=int(os.environ.get("KORA_CHUNK_OVERLAP", self.chunk_overlap)),
            indexing_enabled=_env_bool("KORA_INDEXING_ENABLED", self.indexing_enabled),
            replace_on_success=_env_bool("KORA_INDEXING_REPLACE_ON_SUCCESS", self.replace_on_success),
            index_metadata_sqlite_enabled=_env_bool(
                "KORA_INDEX_METADATA_SQLITE", self.index_metadata_sqlite_enabled
            ),
            index_metadata_db_path=os.environ.get(
                "KORA_INDEX_METADATA_DB_PATH", self.index_metadata_db_path
            ),
            retrieval_enabled=_env_bool("KORA_RETRIEVAL_ENABLED", self.retrieval_enabled),
            retrieval_top_k=int(os.environ.get("KORA_RETRIEVAL_TOP_K", self.retrieval_top_k)),
            indexing_event_topics=self.indexing_event_topics,
            graph_enabled=_env_bool("KORA_GRAPH_ENABLED", self.graph_enabled),
            graph_provider=os.environ.get("KORA_GRAPH_PROVIDER", self.graph_provider),
            graph_store_sqlite_enabled=_env_bool(
                "KORA_GRAPH_STORE_SQLITE", self.graph_store_sqlite_enabled
            ),
            graph_store_db_path=os.environ.get(
                "KORA_GRAPH_STORE_DB_PATH", self.graph_store_db_path
            ),
            graphify_base_url=os.environ.get("KORA_GRAPHIFY_BASE_URL", self.graphify_base_url),
            graphify_api_key=os.environ.get("KORA_GRAPHIFY_API_KEY", self.graphify_api_key),
            graphify_timeout_seconds=float(
                os.environ.get("KORA_GRAPHIFY_TIMEOUT_SECONDS", self.graphify_timeout_seconds)
            ),
            graphify_retry_attempts=int(
                os.environ.get("KORA_GRAPHIFY_RETRY_ATTEMPTS", self.graphify_retry_attempts)
            ),
            graph_export_path=os.environ.get("KORA_GRAPH_EXPORT_PATH", self.graph_export_path),
            graph_event_topics=self.graph_event_topics,
        )


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}
