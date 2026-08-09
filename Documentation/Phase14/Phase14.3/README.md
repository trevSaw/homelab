# Phase 14.3 — Knowledge Platform

**Status:** ✅ Implemented and validated

**Capability:** **KORA can understand and retrieve knowledge.**

## What was implemented

The Phase 14.3 Knowledge Platform per the [canonical
architecture](Knowledge_Platform_Architecture.md). The implementation pipeline:

```text
Knowledge → ingestion → versioning → chunking → embedding → Chroma → retrieval → context → LLM
```

## Components

| Component | Location | Purpose |
| --- | --- | --- |
| `KnowledgeVersion` | `AI/KORA/Knowledge/models/version.py` | Stable document identity + version + SHA-256 content hash |
| `KnowledgeChunk` | `AI/KORA/Knowledge/models/chunk.py` | Deterministic chunk with provenance metadata |
| `IndexMetadata` | `AI/KORA/Knowledge/models/index_state.py` | Vector-index synchronization state |
| `FixedSizeChunker` | `AI/KORA/Knowledge/chunking/fixed_size.py` | Deterministic chunking with overlap |
| `EmbeddingProvider` | `AI/KORA/Knowledge/embedding/interface.py` | Provider abstraction |
| `OllamaEmbeddingProvider` | `AI/KORA/Knowledge/embedding/ollama.py` | Ollama-backed embeddings (config-driven model) |
| `VectorStore` | `AI/KORA/Knowledge/storage/vector.py` | Vector-store abstraction |
| `ChromaVectorStore` | `AI/KORA/Knowledge/storage/chroma.py` | Chroma v2 adapter (infrastructure, non-authoritative) |
| `InMemoryVectorStore` | `AI/KORA/Knowledge/storage/in_memory_vector.py` | Test/local fallback |
| `IndexMetadataStore` | `AI/KORA/Knowledge/storage/index_metadata.py` | SQLite/in-memory sync state |
| `IndexingCoordinator` | `AI/KORA/Knowledge/indexing/coordinator.py` | Event-driven, idempotent, replace-on-success |
| `KnowledgeRetrievalService` | `AI/KORA/Knowledge/retrieval/service.py` | Provenance-aware retrieval |
| `KnowledgeContextAssembler` | `AI/KORA/Knowledge/context/assembly.py` | Knowledge → LLM context |
| `KnowledgeService` | `AI/KORA/Knowledge/service.py` | Facade (ingest/index/retrieve/context) |
| `KnowledgeConfig` | `AI/KORA/Knowledge/config.py` | Configuration (YAML + env) |

## Runtime integration

`AI/KORA/Runtime/app/main.py` builds the KnowledgeService at startup and wires
classification-driven retrieval into the chat path:

- Architecture-style queries: `query_knowledge=True` → Knowledge retrieval +
  context injection.
- Preference/identity/general queries: Knowledge skipped (budget zero).
- Memory and Tools remain off the chat path.
- Retrieval degrades gracefully (empty context, never breaks chat).

## Configuration

`AI/KORA/Config/knowledge_runtime.yaml` with `KORA_*` environment overrides:

- `KORA_EMBEDDING_MODEL` (default `nomic-embed-text`)
- `KORA_CHROMA_BASE_URL` (default `http://chromadb:8000`)
- `KORA_CHROMA_COLLECTION` (default `kora_knowledge`)
- `KORA_INDEX_METADATA_DB_PATH` (default `/data/knowledge-index.sqlite3`)

## Deployment

`services/kora/compose.yaml` now includes a self-contained `chromadb` service
(`kora-chromadb`) on the shared `ollama-net`, plus the KORA image bundles the
`Knowledge` package. Image: `homelab/kora-runtime:14.3.0`.

## Validation

See `Validation/Phase14.3/` for test results and architecture-compliance
verification.
