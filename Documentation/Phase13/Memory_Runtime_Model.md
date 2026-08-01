# Phase 13.5 — Memory & Knowledge Runtime Model

**Status:** ✅ Complete (2026-08-01)  
**Scope:** Architecture and specification only (no databases, embeddings, RAG, ingestion services, or runtime deployments)

---

## Objective

Define how KORA maintains continuity, evolves knowledge, and assembles the right context for reasoning—while preserving governance, explainability, and user control.

---

## Completed

### Documents created

| Document | Purpose |
| --- | --- |
| `Architecture/ai/Memory_Runtime.md` | Memory categories, lifecycle, governance |
| `Architecture/ai/Knowledge_Runtime.md` | Acquisition, validation, updates, promotion pipeline |
| `Architecture/ai/Context_Assembly.md` | Context composition, priority, provenance, limits |
| `Documentation/Phase13/Memory_Runtime_Model.md` | This report |

### Documents updated

| Document | Change |
| --- | --- |
| `Architecture/ai/Memory.md` | Points to runtime; user-control principle |
| `Architecture/ai/Knowledge.md` | Runtime companion + document map |
| `Architecture/ai/KORA.md` | Context Assembly section expanded; runtime pointers |
| `Architecture/ai/Tools.md` | Governance pointers to runtimes / context assembly |
| `Architecture/ai/Agents.md` | Memory/Knowledge runtime governance pointers |
| `Architecture/ai/README.md` | Index and separation table |
| `Architecture/ai/FuturePlans.md` | 13.5 marked complete |
| `Documentation/Phase13/Phase13_Roadmap.md` | Phase 13.5 complete |
| `Documentation/Phase13/README.md` | Link + status |
| `Architecture/standards/StandardsRoadmap.md` | Phase 13.5 status aligned |

---

## Architectural decisions

### Memory lifecycle

`Capture → Evaluate → Classify → Store → Retrieve → Use → Review → Expire/Update/Forget`

Categories: User, Project, Operational, Temporary Context.  
**User controls personal memory.** Secrets never stored.

### Knowledge runtime

Promotion pipeline:

`Information → Candidate → Validated → Authoritative`

Hard rules:

- Memory ↛ Knowledge silently
- Tool results ↛ Knowledge silently
- Generated content requires evaluation

### Context assembly

Combines request, conversation, memory, knowledge, tools, selection metadata, and agent results into provenance-labeled KORA Context.  
Priority is situational; conflicts are dual-cited, not silently resolved.

### Governance model

Provenance required for important fragments.  
Substrate informs reasoning; Council/KORA decide.  
Phase 12 baseline remains authoritative for infrastructure reference claims.

---

## Deferred

| Item | Why deferred |
| --- | --- |
| Database selection (vector/relational/graph) | Tech forbidden in 13.5 |
| Embedding strategy | Tech forbidden |
| Retrieval/RAG implementation | Implementation track |
| Ingestion pipelines | Implementation track |
| Runtime deployment / Docker services | Explicitly out of scope |
| UX surfaces for memory editing | Phase 13.6 |

---

## Consistency checklist

| Requirement | Status |
| --- | --- |
| Memory ≠ Knowledge ≠ Tools ≠ Agents ≠ Council | Explicit |
| No silent promotion across stores | Explicit |
| No tech lock-in | Honored |
| Aligns with prior Phase 13 docs | Explicit |

---

## Next Phase recommendation

**Recommended next step: Phase 13.6 — User Experience**

### Dependency rationale

1. Continuity, knowledge, tools, agents, and Council contracts are now specified.
2. UX needs provenance, memory controls, dissent transparency, and explainability hooks that 13.5 defines.
3. Implementation of stores/tools can proceed later under ADRs without blocking UX architecture.
4. Closing Phase 13 documentation with UX completes the “architecture before implementation” arc for Brainiac/KORA.
