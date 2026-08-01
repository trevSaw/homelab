# Phase 13.2 — Knowledge Architecture Model

**Status:** ✅ Complete (2026-08-01)  
**Scope:** Architecture and specification only (no software, Docker, databases, vector stores, RAG, or ingestion services)

---

## Objective

Define what information KORA reasons from:

- What is KORA’s knowledge?
- How is it organized?
- How is relevant knowledge retrieved?
- How does Council reasoning consume it?
- How is it maintained?
- How is incorrect or outdated knowledge prevented from silently driving decisions?

---

## Completed

### Documents created

| Document | Purpose |
| --- | --- |
| `Architecture/ai/Knowledge.md` | Canonical Knowledge Architecture |
| `Documentation/Phase13/Knowledge_Architecture_Model.md` | This report |

### Documents updated

| Document | Change |
| --- | --- |
| `Architecture/ai/Memory.md` | Explicit Memory ≠ Knowledge boundary; role clarified |
| `Architecture/ai/KORA.md` | Knowledge subsystem ownership; context assembly provenance; epistemic link |
| `Architecture/ai/README.md` | Knowledge entry in index and separation table |
| `Architecture/ai/FuturePlans.md` | 13.2 marked complete in sequence |
| `Documentation/Phase13/Phase13_Roadmap.md` | Phase 13.2 complete |
| `Documentation/Phase13/README.md` | Link + status |
| `Architecture/standards/StandardsRoadmap.md` | Phase 13.2 status aligned |

---

## Architectural decisions

### Knowledge boundaries

- **Knowledge** = what information exists (reference corpus).
- **Memory** = what KORA remembers (continuity / learned interaction context).
- **Tools** = what is true in the environment now.
- Knowledge informs reasoning; **Knowledge does not make decisions.**
- Chat recollection is not authoritative Knowledge.

### Knowledge domains

Conceptual domains defined:

- Infrastructure
- Project
- Technical
- Personal (promoted reference only)
- External (stricter authority/freshness)

### Knowledge lifecycle

`Acquire → Validate → Organize → Index → Retrieve → Provide Context → Review / Update`

Each stage has purpose, responsibility, and governance concerns. No implementation technology selected.

### Retrieval philosophy

- Classification-driven relevance (not similarity-only).
- KORA owns requirement derivation and retrieval initiation.
- Members may request additional knowledge mid-deliberation.
- Conflicts resolved by authority/supersession/transparency—not silent preference.
- Epistemic states required: *I know / I have evidence / I believe / I need more information*.

### Quality model

Accuracy, freshness, authority, context applicability, and confidence are mandatory evaluation axes for decision-grade use.

### Governance model

- Authority tiers (authoritative → deprecated)
- Source ownership via repository (and declared external owners)
- KORA flags; humans approve authoritative mutations
- Deprecated material retained for history but excluded from default current-truth retrieval
- Promotion Memory → Knowledge requires governance

### Relationship model (conceptual)

KORA should support relationships among documents, projects, services, decisions, systems, and concepts. **No graph database selected.**

### Council integration

Knowledge supplies shared source material; Council specialties judge and trade off; KORA synthesizes. Aligns with Dynamics / Deliberation / Selection.

---

## Deferred

| Item | Why deferred |
| --- | --- |
| Vector database selection | Explicitly out of scope |
| Embedding models | Tech selection forbidden in 13.2 |
| Search / RAG frameworks | Implementation track |
| Ingestion pipelines / services | Implementation track |
| Docker / runtime deployables | Explicitly out of scope |
| Deep memory lifecycle runtime | Phase 13.5 |
| MCP live integrations | Phase 13.4 |
| Agent orchestration runtime | Phase 13.3 |
| Automated freshness crawlers | Future implementation |

---

## Consistency checklist

| Requirement | Status |
| --- | --- |
| Knowledge ≠ Memory | Explicit in Knowledge.md / Memory.md / KORA.md |
| Knowledge is a KORA subsystem | Explicit |
| Does not contradict Council operational model | Retrieval hooks into classification → context → deliberation |
| No tech lock-in | Honored |
| Repository remains interim substrate | Affirmed |

---

## Next Phase recommendation

**Recommended next step: Phase 13.3 — Agent Orchestration**

### Dependency rationale

1. Knowledge and Council operational contracts are now defined; orchestration can consume them without inventing retrieval philosophy.
2. Agents must be specified as **temporary execution entities** distinct from Council members—before MCP wiring or runtime memory stores.
3. Phase 13.4 (MCP) and 13.5 (runtime memory/knowledge) depend on clear agent vs tool vs knowledge boundaries that 13.3 should lock.

### Alternate acceptable sequencing

If tool-backed live truth is blocking architecture clarity sooner than agents, **13.4 External Integrations** may proceed in parallel *only* as architecture/spec for MCP boundaries—not as deployments—while still treating agents as non-Council workers.

Default recommendation remains **13.3** to prevent agent/Council conflation before integrations multiply.
