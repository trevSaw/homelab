# Knowledge Ingestion Foundation (Phase 14.2C)

**Objective**
Create a governed, provider‑neutral ingestion pipeline for external reference material.  Knowledge documents are stored via a pluggable ``KnowledgeStore`` abstraction and are isolated from the existing Memory runtime and approval workflow.

**Architecture**
```
User / System Source
    │
    ▼
knowledge.ingestion.file event (via shared EventBus)
    │
    ▼
KnowledgeIngestionService (internal Python component)
    │   └─→ KnowledgeProcessor → KnowledgeDocument
    ▼
KnowledgeStore (in‑memory now, replaceable later)
    │
    ▼
Knowledge storage (future adapters: SQLite, vector DB, etc.)
```

* Uses the existing internal ``EventBus`` with a distinct ``knowledge.*`` namespace.
* No FastAPI routes – ingestion is an internal service.
* Memory runtime, Approval Engine, and DurableMemoryStore remain untouched.

**Key components**
* ``KnowledgeDocument`` – immutable dataclass (content, source, metadata, deterministic ``doc_id``).
* ``KnowledgeIngestionEvent`` – ``EventEnvelope`` with ``event_type='knowledge.ingestion.file'``.
* ``KnowledgeProcessor`` – reads local files, extracts minimal metadata.
* ``KnowledgeStore`` protocol – async ``save``, ``list_documents``, ``find_by_id``.
* ``InMemoryKnowledgeStore`` – test implementation.
* ``KnowledgeIngestionService`` – public façade used by internal callers.

**Test strategy**
* Unit tests for ``process_ingestion`` (file reading, metadata extraction, duplicate handling).
* Tests for ``InMemoryKnowledgeStore`` CRUD behavior.
* End‑to‑end test for ``KnowledgeIngestionService`` ensuring a document is stored and the correct ``knowledge.ingestion.file`` event is published (mock ``EventBus`` to assert publish call).
* All existing Phase 14.2A/B tests must continue to pass.

**Documentation updates**
* Add ``Documentation/Phase14/Phase14.2C/README.md`` (this file) describing the foundation and boundaries.
* Update road‑map entry for Phase 14.2C and ensure the sequence:
  14.2A → 14.2B → 14.2C → 14.2D → 14.3.
* No changes to Phase 14.2B docs that would skip Phase 14.2D.

**Boundary verification**
* Knowledge ingestion publishes on ``knowledge.*`` – Memory runtime only subscribes to ``memory.*``.
* No code imports from ``AI/KORA/Runtime``; imports are one‑way (Knowledge → EventBus only).
* Storage implementation is independent; ``KnowledgeStore`` does not implement ``DurableMemoryStore``.

**Risks / open questions**
* Duplicate detection – currently based on deterministic ``doc_id`` (SHA‑256 of content).  Collisions are astronomically unlikely.
* Future storage adapters may need migration scripts – out of scope for this phase.
* Ensure test coverage does not inadvertently start a FastAPI server – all services are pure Python.

---
*Next phase entry point*: **Phase 14.2D — Production Validation** (will exercise the full ingestion pipeline under production‑like conditions before moving to the Knowledge Runtime phase).
