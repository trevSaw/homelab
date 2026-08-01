# Phase 13.9 — Vertical Slice Model

**Status:** ✅ Complete (2026-08-01)  
**Scope:** Architecture validation of a minimal end-to-end KORA flow (no deploys, installs, or compose)

---

## Objective

Validate Phase 13.0–13.8 architecture by defining a **thin vertical slice**: the minimum workflow and interface contracts that prove components can compose without collapsing boundaries.

Technology candidates remain ADR-governed. This phase does **not** install Open WebUI, Hermes, Honcho, ChromaDB, or Graphify.

---

## Created documents

| Document | Purpose |
| --- | --- |
| `Architecture/ai/Vertical_Slice.md` | Minimum E2E workflow, inputs/outputs, boundaries, provenance, failure handling |
| `Architecture/ai/Prototype_Boundaries.md` | Allowed vs forbidden prototype proofs |
| `Architecture/ai/Integration_Flow.md` | Conceptual data movement, ownership, provenance preservation |
| `Documentation/Phase13/Vertical_Slice_Model.md` | This report |

---

## Architectural decisions

1. **Slice shape:** User Request → Interface → Orchestration → KORA Classification → Council Selection → Context Assembly → Knowledge/Memory Retrieval → Council Deliberation → Recommendation → Explainability Output.
2. **KORA remains conductor** — orchestration/UI candidates are substrates, not product identity.
3. **Memory and Knowledge retrieval are separate channels** with mandatory provenance labels.
4. **Tools and agents are optional** on the thin-slice default path; Execute/Administrative actions are refused.
5. **Graphify remains off the default path** (ADR-0007 Defer).
6. **No durable Memory writes** without governance in prototype scope.
7. **Technology neutrality** — interfaces defined architecturally; not rewritten around vendor APIs.
8. **Preserved separations:** Council ≠ Agents; Memory ≠ Knowledge; Knowledge ≠ Tools; Tools ≠ Decisions.

---

## Deferred implementation

| Item | Status |
| --- | --- |
| Docker / compose / service installs | Deferred (forbidden in 13.9) |
| Hermes / Open WebUI / Honcho / ChromaDB / Graphify runtime | Deferred to authorized spike |
| Live MCP / Execute tooling | Deferred |
| Permanent Memory write path | Deferred pending governance UX |
| Knowledge promotion pipeline automation | Deferred |
| Relationship graph integration | Deferred (ADR-0007) |
| Production automation | Deferred |

---

## Technology boundaries

| Candidate | ADR | Role in slice |
| --- | --- | --- |
| Open WebUI | 0008 Provisional Adopt | Future UI only; not KORA |
| Hermes | 0004 Provisional Adopt | Future orchestration substrate behind façade |
| Honcho | 0005 Spike | Future Memory read-path candidate; no ungated writes |
| ChromaDB | 0006 Provisional Adopt | Future Knowledge retrieval index; not SoT |
| Graphify | 0007 Defer | Out of default thin slice |

---

## Readiness assessment for implementation

| Question | Assessment |
| --- | --- |
| End-to-end flow defined? | ✅ `Vertical_Slice.md` |
| Component boundaries explicit? | ✅ slice + integration + prototype boundaries |
| Technology coupling introduced? | ✅ Avoided — candidates mapped, not required |
| Prototype scope controlled? | ✅ Allowed/Not allowed lists |
| Implementation risks documented? | ✅ Integration_Flow risk table + ADR constraints |
| Ready to install now? | ❌ Not authorized by 13.9 |
| Ready to plan a constrained spike? | ✅ Yes — next phase may authorize spike planning against these interfaces |

**Verdict:** Architecture is ready for a **later, explicitly authorized non-production spike plan**. It is not ready for deployment or compose.

---

## Consistency checks

| Requirement | Status |
| --- | --- |
| Does not rewrite 13.0–13.8 architecture | Reference updates only |
| Preserves Council/Memory/Knowledge/Tools separations | Explicit in all three specs |
| No Docker/compose/installs | Confirmed |
| ADR posture unchanged | Referenced only |

---

## Recommended next phase

Authorize **spike planning** (not production): map Vertical_Slice interfaces to ADR-0004/0008 façade constraints, stub Memory/Knowledge read channels, and define acceptance tests from `Prototype_Boundaries.md`—still without Phase 12 impact until a dedicated implementation phase says otherwise.
