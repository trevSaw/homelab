# Phase 14.4 — Knowledge Graph / Graphify

**Status:** ✅ Implemented and validated

**Capability:** **KORA can understand relationships between knowledge.**

## Architecture

Phase 14.4 extends the Phase 14.3 Knowledge Platform with a relationship layer.
The resulting architecture:

```text
                    ┌───────────────┐
                    │   Knowledge   │
                    │  Authority    │
                    └───────┬───────┘
                            │
               ┌────────────┴────────────┐
               │                         │
               ▼                         ▼
        Semantic Index             Knowledge Graph
               │                         │
               ▼                         ▼
            Chroma                   Graphify
               │                         │
               └────────────┬────────────┘
                            │
                            ▼
                    Retrieval / Context
                            │
                            ▼
                           LLM
```

- **Chroma** answers *"what knowledge is semantically similar?"*
- **Graphify** answers *"what things are connected?"*
- Neither replaces the other; neither is the Knowledge authority.

## Authority boundaries

- **Knowledge ≠ Memory** — graph relationships are never stored as Memory; no
  auto-promotion between graph and Memory.
- **Graphify ≠ Chroma** — Graphify is a relationship graph (entities, edges,
  traversal); Chroma is a vector index. Graphify does not do embeddings.
- **Open WebUI ≠ Knowledge authority** — Open WebUI is the UI layer only.
- **EventBus remains canonical** — graph indexing is triggered by
  `knowledge.ingestion.file` events on the existing EventBus.

## Graph data model

- **GraphEntity** — entity_id (deterministic from type+name), entity_type,
  canonical_name, aliases, source_knowledge_id, source_version,
  source_content_hash, source_ref.
- **GraphRelationship** — relationship_id (deterministic), source_entity,
  relationship_type, target_entity, source_knowledge_id, confidence
  (EXTRACTED/INFERRED), provenance.

Every graph object retains provenance to its authoritative Knowledge.

## Extraction

Deterministic rule-based extraction mirrors Graphify's markdown extractor:
- one entity per document (type `document`)
- one entity per markdown heading
- `contains` relationships for heading hierarchy
- `references` relationships for inline links, reference-style links, and
  `[[wikilinks]]` (all EXTRACTED)

No LLM is required for extraction; it is deterministic, idempotent, and
provenance-preserving.

## Pipeline

```text
Knowledge change
    ↓
 EventBus (knowledge.ingestion.file)
    ↓
 GraphIndexingCoordinator
    ↓
 entity/relationship extraction
    ↓
 GraphStore (KORA-owned, SQLite/in-memory)
    ↓
 Graphify (export graph.json → MCP HTTP serve)
```

## Retrieval

- **GraphRetrievalService** — KORA-owned; entity lookup, neighbors, relationships,
  provenance; graceful degradation on failure.
- **CombinedRetrievalService** — orchestrates semantic (Chroma) + graph (Graphify)
  retrieval without hard-wiring them together.
- **GraphContextAssembler** — composes Knowledge evidence + graph relationships
  into a provenance-labeled context block.

## Runtime integration

Architecture-style queries now select both `knowledge` and `graphify` stores.
Memory and Tools remain off the chat path. Graph backend failure degrades to
semantic-only retrieval.

## Deployment

Independent Compose projects (shared external `ollama-net`):

- `services/kora/` — KORA Runtime (`homelab/kora-runtime:14.4.0`)
- `services/chromadb/` — Chroma vector index (reuses existing data volume)
- `services/graphify/` — Graphify MCP HTTP server (`homelab/graphify:14.4.0`)

Graphify serves KORA's derived graph (`/data/graph.json`) over MCP Streamable
HTTP with `--json-response`.

## Files

| Area | Location |
| --- | --- |
| Graph models | `AI/KORA/Knowledge/graph/models.py` |
| GraphStore | `AI/KORA/Knowledge/graph/{in_memory_store,sqlite_store}.py` |
| Extraction | `AI/KORA/Knowledge/graph/extraction.py` |
| Indexing | `AI/KORA/Knowledge/graph/indexing.py` |
| Graphify client | `AI/KORA/Knowledge/graph/graphify.py` |
| Graphify export | `AI/KORA/Knowledge/graph/export.py` |
| Retrieval | `AI/KORA/Knowledge/graph/{retrieval,combined}.py` |
| Context | `AI/KORA/Knowledge/context/graph_context.py` |
