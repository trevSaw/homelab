# Knowledge domain for KORA

Phase 14.3 — Knowledge Platform: **KORA can understand and retrieve knowledge.**
Phase 14.4 — Knowledge Graph: **KORA can understand relationships between
knowledge.**

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
- **GraphEntity / GraphRelationship** – deterministic graph model with provenance.
- **GraphStore** – SQLite/in-memory persistence of the derived graph.
- **Graph extraction** – deterministic markdown entity/relationship extraction.
- **GraphIndexingCoordinator** – event-driven, idempotent graph synchronization.
- **GraphifyClient / export** – MCP HTTP client + `graph.json` export for Graphify.
- **GraphRetrievalService / CombinedRetrievalService** – graph and combined
  semantic+graph retrieval.
- **GraphContextAssembler** – graph-aware provenance-labeled context.

## Boundaries

- Knowledge ≠ Memory. No automatic promotion in either direction.
- Chroma is a semantic index; Graphify is a relationship graph; neither is the
  Knowledge authority.
- Open WebUI is the UI layer and is not a Knowledge authority.
- Graphify is complementary to Chroma (Phase 14.4).

## Configuration

`AI/KORA/Config/knowledge_runtime.yaml` plus `KORA_*` environment overrides
(including `KORA_GRAPH_*`, `KORA_GRAPHIFY_*`).
See `Documentation/Phase14/Phase14.3/` and `Documentation/Phase14/Phase14.4/`.
