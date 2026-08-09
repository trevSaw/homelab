# Knowledge domain for KORA

Phase 14.3 — Knowledge Platform: **KORA can understand and retrieve knowledge.**

## Components

- **KnowledgeDocument** – immutable representation of a knowledge source.
- **KnowledgeVersion** – stable document identity + version + content hash.
- **KnowledgeChunk** – deterministic segment with full provenance metadata.
- **Ingestion pipeline** – reads local files, stores documents, publishes
  `knowledge.ingestion.file` events.
- **Chunking** – deterministic fixed-size chunker with overlap.
- **Embedding provider** – Ollama-backed, config-driven model
  (`KORA_EMBEDDING_MODEL`, default `nomic-embed-text`).
- **VectorStore abstraction** – KORA depends on this, not on Chroma directly.
- **ChromaVectorStore** – Chroma v2 adapter (infrastructure; not Knowledge
  authority).
- **Index metadata store** – SQLite/in-memory synchronization state.
- **Indexing coordinator** – event-driven, idempotent, replace-on-success.
- **Retrieval service** – provenance-aware, top-k, filtering, graceful
  degradation.
- **Context assembly** – knowledge → provenance-labeled LLM context.

## Boundaries

- Knowledge ≠ Memory. No automatic promotion in either direction.
- Chroma is an index/retrieval layer; the authoritative Knowledge model remains
  inside KORA.
- Open WebUI is the UI layer and is not a Knowledge authority.
- Graphify (Phase 14.4) is complementary to Chroma and not implemented here.

## Configuration

`AI/KORA/Config/knowledge_runtime.yaml` plus `KORA_*` environment overrides.
See `Documentation/Phase14/Phase14.3/`.
