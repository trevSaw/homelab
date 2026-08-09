# Phase 14.3 — Knowledge Platform Architecture

**Status:** ✅ Ratified (canonical implementation contract for Phase 14.3)
**Phase:** Phase 14.3 — Knowledge Platform
**Capability:** **KORA can understand and retrieve knowledge.**

This document is the **canonical Phase 14.3 implementation contract**. It
defines what the Knowledge Service owns, how retrieval is performed, how
Knowledge remains separate from Memory, and what is explicitly out of scope for
Phase 14.3. It does not implement anything; it establishes the architectural
contract a future implementation must follow.

**Authoritative companions:**
- `Architecture/ai/Knowledge.md` — Phase 13.2 domains, quality, governance principles
- `Architecture/ai/Knowledge_Runtime.md` — Phase 13.5 conceptual runtime
- `Architecture/decisions/ADR-0006-Knowledge-Retrieval-ChromaDB.md` — ChromaDB evaluation/decision
- `Architecture/decisions/ADR-0007-Relationship-Layer-Graphify.md` — Graphify evaluation/decision (Phase 14.4)
- `AI/OpenWebUI/Config/sot_boundaries.yaml` — Open WebUI SoT boundaries (ADR-0008)
- `Documentation/Phase14/Phase14_Roadmap.md` — Phase 14 roadmap

---

## Terminology transition

> "Knowledge Runtime" is the terminology used by the historical Phase 13
> architecture. "Knowledge Service" is the ratified Phase 14.3 terminology for
> the same logical service.

Historical Phase 13 documents retain "Knowledge Runtime" and are **not**
rewritten merely to rename the term. New Phase 14.3 documentation uses
**Knowledge Service**.

---

## 1. Knowledge Service Boundary

The **Knowledge Service owns the Knowledge lifecycle**. It is responsible for:

- `KnowledgeDocument`
- document identity
- provenance
- metadata
- ingestion
- normalization
- chunking
- versioning
- content hashing
- embedding orchestration
- index lifecycle
- retrieval policy
- filtering
- ranking
- provenance handling
- stale-index detection
- Knowledge events
- RAG context construction

> **KORA owns what Knowledge means and how Knowledge is used.**

The Knowledge Service is part of KORA's architecture. It is one of three
logical services (Memory, Knowledge, Tool) orchestrated by the KORA Runtime.

---

## 2. ChromaDB Boundary

ChromaDB is an **infrastructure/indexing component**.

ChromaDB is responsible for:

- vector storage
- similarity search
- metadata filtering
- collections
- persistence

ChromaDB is **NOT the Knowledge authority**. ChromaDB must not determine:

- whether a document is authoritative
- whether a document is current
- whether a document should be indexed
- whether something is Memory
- how RAG works
- how retrieved results affect KORA

The authoritative Knowledge model remains within KORA's governed Knowledge
domain.

> **If ChromaDB disappears, KORA's Knowledge model must still make sense.**

Consistent with ADR-0006 (Provisional Adopt): ChromaDB stores/retrieves
embeddings and metadata; repository documents/ADRs remain Source of Truth.

---

## 3. Graphify Boundary

Graphify belongs to **Phase 14.4 — Knowledge Graph**. It is intentionally **not**
implemented in Phase 14.3.

When eventually introduced, Graphify provides the relationship representation of
Knowledge:

```text
Knowledge Service
       │
       ├── ChromaDB
       │     semantic/vector representation
       │
       └── Graphify
             relationship representation
```

- ChromaDB answers: **What knowledge is semantically similar?**
- Graphify answers: **What things are connected?**

Graphify does not replace ChromaDB. ChromaDB does not replace Graphify. Neither
becomes the authoritative Knowledge source. The Knowledge Service owns both
integrations.

Consistent with ADR-0007 (Accepted for Future Implementation, Phase 14.4).

---

## 4. Embedding Strategy

Phase 14.3 uses an **Ollama-backed embedding provider**.

```text
Knowledge Service
       │
       │ embedding request
       ▼
     Ollama
       │
       ▼
 embedding vector
       │
       ▼
    ChromaDB
```

- **Do not introduce a separate embedding service in Phase 14.3.**
- The embedding model must be **configuration-driven** — not hard-coded around a
  specific model name:

```text
KORA_EMBEDDING_MODEL=<configured model>
```

- The Knowledge Service depends on an **embedding abstraction/provider** rather
  than making the entire Knowledge architecture depend on Ollama-specific
  semantics.
- **Do not implement multiple embedding providers during Phase 14.3.** The
  approved initial provider is Ollama. Future providers may be introduced later
  without changing the Knowledge abstraction.

---

## 5. Index Lifecycle

The approved lifecycle:

```text
INGEST
  ↓
NORMALIZE
  ↓
IDENTIFY
  ↓
VERSION
  ↓
CHUNK
  ↓
EMBED
  ↓
INDEX
  ↓
READY
```

### Document identity and versioning

Documents use stable identity. Distinguish conceptually:

```text
document_id
document_version
content_hash
```

Content changes create a new version of the same Knowledge document.

### Change detection

Use deterministic content hashing:

```text
document content
      ↓
    SHA-256
      ↓
 content_hash
```

- Same hash: existing document + same content hash → **no re-embedding**.
- Changed hash: existing document + different content hash → **new version** →
  re-chunk → re-embed → re-index.

**Filesystem timestamps must NOT be treated as the authoritative change
detector.**

### Chunk identity

Indexed chunks retain enough metadata to establish their origin. At minimum the
architecture accounts for:

```text
document_id
document_version
chunk_id
content_hash
embedding_model
```

This allows retrieval results to retain provenance.

### Stale index handling — replace-on-success

Do not destroy the currently usable index before a replacement has successfully
been generated:

```text
Current index
     │
     ├───────────────┐
     │               │
     │          Build new index
     │               │
     │          Embed new chunks
     │               │
     │          Write successfully
     │               │
     └───────────────┘
                     │
                     ▼
              Promote new index
                     │
                     ▼
              Retire old index
```

If embedding or indexing fails, the existing usable index remains available.

---

## 6. Retrieval Flow

KORA owns retrieval.

```text
User
 │
 ▼
Open WebUI
 │
 ▼
KORA Runtime
 │
 ▼
Knowledge Service
 │
 ├── query normalization
 ├── filters
 ├── retrieval
 ├── ranking
 └── provenance
 │
 ▼
Knowledge Results
 │
 ▼
RAG Context
 │
 ▼
KORA Runtime
 │
 ▼
LLM
 │
 ▼
Response
```

- ChromaDB provides vector retrieval **candidates**.
- The Knowledge Service owns the **retrieval policy**.
- KORA determines: what to search, which filters apply, how many results to
  retrieve, ranking policy, provenance handling, and context construction.
- ChromaDB does not own the complete retrieval strategy.

---

## 7. Memory Boundary (non-negotiable)

Knowledge and Memory remain independent domains.

```text
                  KORA Runtime
                  /          \
                 /            \
                ▼              ▼
        Knowledge Service   Memory Service
                │              │
             Chroma          Honcho
```

- Knowledge retrieval is a **read/retrieval** operation.
- Memory remains: **PROPOSE → APPROVE → COMMIT**.
- A Knowledge result must **never automatically become Memory**.
- Storing something in Memory must **not automatically create Knowledge**.
- **No automatic promotion exists between the two domains.**

Consistent with `Knowledge.md`, `Memory.md`, `Knowledge_Runtime.md`, and
`Memory_Approval_UX.md`.

---

## 8. RAG Boundary

**Basic RAG is part of Phase 14.3.** Phase 14.3 finishes with:

> **KORA can answer a question using retrieved Knowledge.**

```text
Question
   │
   ▼
Retrieve Knowledge
   │
   ▼
Rank / Filter
   │
   ▼
Construct Knowledge Context
   │
   ▼
Send context to LLM
   │
   ▼
Grounded response
```

Phase 14.3 includes: semantic retrieval, metadata filtering, basic ranking,
context construction, provenance, prompt/context injection, and grounded
response generation.

Phase 14.3 **does not include**: agentic retrieval, autonomous search loops,
graph reasoning, graph retrieval, multi-hop graph traversal, Council reasoning,
autonomous agents, sophisticated autonomous query planning, or Tool execution.

**Do not create a separate "RAG phase."**

---

## 9. Open WebUI Relationship

Open WebUI remains the **UI/presentation layer**. KORA owns Knowledge queries.

```text
Open WebUI
     │
     ▼
KORA Runtime
     │
     ▼
Knowledge Service
     │
     ▼
ChromaDB
     │
     ▼
Knowledge Context
     │
     ▼
KORA
     │
     ▼
Ollama
```

- Open WebUI must not become a competing Knowledge authority.
- Open WebUI may eventually provide UI functionality: document upload,
  knowledge browsing, search UI, citation display, source display, user
  controls. Those operations should ultimately interact with KORA's Knowledge
  architecture.

Consistent with ADR-0008 and `AI/OpenWebUI/Config/sot_boundaries.yaml`.

---

## 10. Open WebUI RAG — no competing path

**Do not establish two competing RAG systems.**

Avoid:

```text
Open WebUI RAG
      +
KORA RAG
```

The authoritative Knowledge retrieval path is:

```text
Open WebUI
     │
     ▼
KORA
     │
     ▼
Knowledge Service
     │
     ▼
ChromaDB
     │
     ▼
Knowledge Context
     │
     ▼
KORA
     │
     ▼
Ollama
```

Open WebUI displays the result. KORA owns retrieval.

---

## 11. Canonical Phase 14.3 Architecture

```text
                                  USER
                                    │
                                    ▼
                              ┌───────────┐
                              │ Open WebUI│
                              │    UI     │
                              └─────┬─────┘
                                    │
                                    ▼
                           ┌─────────────────┐
                           │   KORA Runtime  │
                           │  Orchestration  │
                           └────────┬────────┘
                                    │
                         ┌──────────┴──────────┐
                         │                     │
                         ▼                     ▼
                  Memory Service        Knowledge Service
                         │                     │
                      Honcho          ┌────────┼────────┐
                                     │        │        │
                                     ▼        ▼        ▼
                                Embeddings  Chroma  Sources
                                     │
                                   Ollama
```

Future Phase 14.4 adds:

```text
Knowledge Service
       │
       ├── ChromaDB
       │     semantic/vector representation
       │
       └── Graphify
             relationship representation
```

---

## 12. Phase Ownership Boundaries

### Phase 14.3 owns

- Knowledge Service runtime ownership
- embeddings
- Ollama embedding integration
- ChromaDB integration
- incremental indexing
- document versioning
- stale-index handling
- retrieval APIs
- provenance-aware retrieval
- basic RAG
- Knowledge context construction
- production validation

### Phase 14.4 owns

- Graphify
- entity extraction
- relationship extraction
- graph synchronization
- graph queries
- graph visualization
- hybrid vector/graph retrieval

### Phase 14.5 owns

- Tool Service
- MCP
- local tools
- external APIs
- tool registry
- permissions
- Open WebUI tool integration

### Phase 15 owns

- Council
- deliberation
- Council orchestration
- synthesis
- hardware-flexible intelligence

### Phase 16 owns

- autonomous workflows
- governed execution
- automation
- long-running workflows
- self-healing proposals
- autonomous planning

**No later-phase capability leaks into Phase 14.3.**

---

## 13. Phase 14.3 Non-Goals (explicit)

Phase 14.3 does **not** include:

- Graph reasoning / graph retrieval / multi-hop graph traversal (Phase 14.4)
- Graphify integration (Phase 14.4)
- Agentic retrieval
- Autonomous search loops
- Sophisticated autonomous query planning
- Council reasoning (Phase 15)
- Autonomous agents (Phase 16)
- Tool execution (Phase 14.5)
- MCP integration (Phase 14.5)
- A separate embedding service
- A separate "RAG phase"
- A competing Open WebUI RAG path

---

## 14. Documentation Objective

This contract answers for a future implementation engineer:

1. What does the Knowledge Service own? — §1
2. What does ChromaDB own? — §2
3. What will Graphify own? — §3
4. How are embeddings generated? — §4
5. How are documents versioned? — §5
6. How are stale indexes handled? — §5
7. Where does retrieval occur? — §6
8. Where does RAG occur? — §8
9. How does Knowledge remain separate from Memory? — §7
10. What role does Open WebUI play? — §9
11. What is explicitly outside Phase 14.3? — §12, §13
