# Phase 14.3 — Architecture Compliance Audit

**Method:** Code inspection + runtime verification.

## Boundaries

| # | Requirement | Evidence | Result |
| --- | --- | --- | --- |
| 1 | Knowledge never imports Memory | `AI/KORA/Knowledge/**` imports `app.event_bus`, its own modules; no `app.memory_*` | ✅ |
| 2 | Memory never imports Knowledge | `app/memory_runtime.py` unchanged; no Knowledge imports | ✅ |
| 3 | Chroma is not the Knowledge authority | Metadata/store in KORA (`IndexMetadataStore`); Chroma only holds vectors | ✅ |
| 4 | Graphify not implemented (Phase 14.4) | No Graphify code added | ✅ |
| 5 | Embedding provider replaceable | `EmbeddingProvider` protocol; only Ollama provider wired | ✅ |
| 6 | No separate embedding service | Ollama used directly via provider | ✅ |
| 7 | EventBus is the canonical event mechanism | `IndexingCoordinator` subscribes via existing `EventBus` | ✅ |
| 8 | Replace-on-success indexing | New chunks upserted before stale deleted; failure keeps old index | ✅ |
| 9 | Indexing idempotent | Same version+hash+model → no-op | ✅ |
| 10 | Retrieval preserves provenance | `RetrievedChunk` carries document_id/version/content_hash/source | ✅ |
| 11 | Open WebUI not Knowledge authority | `sot_boundaries.yaml` unchanged; KORA owns retrieval | ✅ |
| 12 | No auto Memory↔Knowledge promotion | Ingestion only publishes `knowledge.*` events | ✅ |

## Runtime verification

- `pytest`: 102 passed.
- Docker image `homelab/kora-runtime:14.3.0` builds; `app.main` + `Knowledge` import.
- `kora` container healthy; `/health` knowledge block reports `status: ok`,
  vector_store `chroma`, vector_healthy true.
- End-to-end: ingest → index → retrieve → context returned provenance-labeled
  knowledge with real Ollama embeddings and real Chroma.
- Chat path: architecture query → `stores_queried: ['knowledge']`;
  preference query → Knowledge skipped, budget 0.
