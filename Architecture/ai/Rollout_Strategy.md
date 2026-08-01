# KORA Production Rollout Strategy

**Status:** Canonical rollout strategy (Phase 13.15)  
**Platform:** KORA / Brainiac (`KORA.md`)  
**Rule:** Staged enablement of production capabilities. No stage rewrites architecture. Solo remains Stage 1.

Companion: `Production_Architecture.md`, `Production_Service_Topology.md`, `Runtime_Profiles.md`

---

## Principles

1. **Contracts first** — each stage must pass Runtime Contracts  
2. **Solo first** — Distributed is last among core stages  
3. **Rollback ready** — every stage has a kill/disable path  
4. **Phase 12 safe** — no regression of production baseline  
5. **Graphify last / optional** — only if ADR-0007 adopts  

---

## Stage 1 — Solo Runtime

**Enable:** Open WebUI + KORA Runtime (co-located Classification / Context Intelligence / Assembly / Solo Council / Explainability); thin Hermes optional.

**Phase 14.1 implementation status:** ✅ Complete — primary path is `Open WebUI → KORA → Ollama` (Hermes not on primary path).

| Field | Content |
| --- | --- |
| **Prerequisites** | Phase 13 architecture complete; Phase 12 baseline stable; ADR-0008/0004 constraints understood |
| **Risks** | UI/orchestration identity capture; skipping Context Intelligence |
| **Rollback** | Disable UI/stack; architecture docs remain; no durable SoT loss — see `Validation/Phase14.1/Rollback_Procedure.md` |
| **Acceptance** | Vertical-slice path works; classify-before-retrieve; KORA identity; refuse Execute; explainability present |

---

## Stage 2 — Simulated Council

**Enable:** Structured multi-member prompting inside Council Runtime / KORA (still single model).

| Field | Content |
| --- | --- |
| **Prerequisites** | Stage 1 acceptance; Dynamics/Selection docs stable |
| **Risks** | Prompt leakage as CoT; fake independence theater |
| **Rollback** | Revert to Solo conceptual Council without UI change |
| **Acceptance** | Disagreement preservable; contributors labeled; members ≠ agents; UX unchanged |

---

## Stage 3 — Memory Runtime

**Enable:** Memory Runtime (Honcho candidate) with approval-gated writes.

| Field | Content |
| --- | --- |
| **Prerequisites** | Stage 1; ADR-0005; Memory UX for approve/correct/delete |
| **Risks** | Silent writes; Memory→Knowledge laundering; secrets in Memory |
| **Rollback** | Disable Memory queries; discard/export candidates; continue without continuity |
| **Acceptance** | Preference/personal strategies Memory-only; no silent durable writes; empty Memory valid |

---

## Stage 4 — Knowledge Runtime

**Enable:** Knowledge Runtime (ChromaDB candidate) indexing governed docs.

| Field | Content |
| --- | --- |
| **Prerequisites** | Stage 1; ADR-0006; ingestion from repo/ADRs/standards |
| **Risks** | Index treated as SoT; preference over-fetch regression |
| **Rollback** | Disable Knowledge queries; fall back to explicit doc pointers / gaps |
| **Acceptance** | Architecture strategies Knowledge-first; provenance/authority present; preference Knowledge budget 0 |

---

## Stage 5 — Tool Runtime

**Enable:** Tool Runtime + MCP Gateway (Read first; Execute gated).

| Field | Content |
| --- | --- |
| **Prerequisites** | Stages 1–2; Tools/MCP architecture; least-privilege plan vs Phase 12 |
| **Risks** | Ungated Execute; Phase 12 blast radius; fabricated live state when tools down |
| **Rollback** | Disable Tools/MCP; operational questions → uncertainty |
| **Acceptance** | Operational strategies Tools-first; unavailable → no fabrication; Execute refused without approval |

---

## Stage 6 — Distributed Council

**Enable:** Independent Council member runtimes under Hermes orchestration.

| Field | Content |
| --- | --- |
| **Prerequisites** | Stages 1–2 strong; ADR-0004 façade proven; observability for member contributions |
| **Risks** | Identity fragmentation; agents confused with members; cost/latency |
| **Rollback** | Fall back to Simulated or Solo; same UI identity |
| **Acceptance** | KORA sole user face; Dynamics preserved; contributions attributable; no Execute via members |

---

## Stage 7 — Relationship Runtime (Graphify if adopted)

**Enable:** Optional Relationship Runtime only after ADR-0007 moves off Defer.

| Field | Content |
| --- | --- |
| **Prerequisites** | ADR-0007 Adopt/Provisional; Stages 4+ recommended |
| **Risks** | Graph as SoT; premature complexity |
| **Rollback** | Disable graph; Knowledge+docs remain |
| **Acceptance** | Complements Knowledge; rebuildable; off path if unhealthy |

---

## Cross-Stage Acceptance (Always)

- Memory ≠ Knowledge ≠ Tools ≠ Council ≠ Agents  
- Context Intelligence precedes retrieval  
- Explainability + provenance  
- No Phase 12 unauthorized mutation  
- Runtime Profiles semantics unchanged  

---

## Document Map

| Document | Role |
| --- | --- |
| `Rollout_Strategy.md` (this file) | Staged enablement |
| `Operational_Readiness.md` | Day-2 ops philosophy |
| `Production_Service_Topology.md` | What gets enabled |
