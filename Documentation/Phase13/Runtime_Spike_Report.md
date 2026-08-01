# Phase 13.11 — Runtime Spike Report

**Status:** ✅ Complete (2026-08-01)  
**Scope:** Non-production disposable lab execution under `/mnt/monarch/prototypes/kora-spike/`  
**Git:** Documentation + validation only (no lab runtime committed)

---

## Objective

Validate that Phase 13 architecture contracts can be implemented without violating Council / Memory / Knowledge / Tools boundaries, using ADR-governed candidates in an isolated laboratory.

---

## Environment

| Item | Value |
| --- | --- |
| Lab root | `/mnt/monarch/prototypes/kora-spike/` |
| Network | `kora_spike_net` (created then removed) |
| Container | `kora-spike-chroma` (`chromadb/chroma:0.6.3`) |
| Publish | `127.0.0.1:18000` only |
| Phase 12 attach | None |
| Secrets | None |
| Graphify | Excluded |

---

## Components tested

| Component | Mode | Result |
| --- | --- | --- |
| Open WebUI | Adapter (identity envelope) | Pass — KORA branding enforced |
| Hermes | Adapter (orchestration substrate) | Pass — not KORA; does not replace Council |
| KORA façade | Implemented | Pass — conductor path |
| Council simulation | Implemented | Pass — selection + ≠ agents |
| Honcho | Adapter (memory workflow) | Pass — candidate staging; no durable write |
| ChromaDB | Real container + adapter | Pass — isolated; not treated as SoT |
| Graphify | Excluded | N/A |

---

## Architecture mapping

| Spike hop | Architecture owner |
| --- | --- |
| User request | User |
| Open WebUI adapter | UI Layer (ADR-0008) |
| Hermes adapter | Orchestration substrate (ADR-0004) |
| KORA façade | Conductor / identity |
| Council simulation | Council Dynamics/Selection |
| Context assembly | `Context_Assembly.md` |
| Memory adapter | Memory Runtime (ADR-0005) |
| Knowledge adapter + Chroma | Knowledge Runtime retrieval (ADR-0006) |
| Explainable response | `Explainability.md` |

---

## Acceptance criteria mapping

Automated scenario runner: **ALL_PASS** (`Validation/Phase13.11/scenario_summary.json`).

| Area | Outcome |
| --- | --- |
| Council boundary | Pass (`agents_as_members=false`; deliberative synthesis) |
| Memory boundary | Pass (no durable write; preference = pending approval) |
| Knowledge boundary | Pass (fixtures labeled; conflict surfaced; not SoT) |
| Tool boundary | Pass (no tool invocation; forbidden action refused) |
| Explainability | Pass (structured object; no raw CoT) |
| Provenance | Pass (labeled evidence) |
| Replaceability | Pass (adapters swappable; Graphify excluded) |
| Runtime isolation | Pass (dedicated net; rolled back) |

---

## Failures

**Hard failures:** none (all six scenarios passed automated checks).

**Findings / soft issues:**

1. **Retrieval over-fetch on preference turns** — keyword Knowledge search returned unrelated HA networking fixtures during the Jellyfin/Plex preference scenario. Memory write boundaries held, but Context Assembly should gate Knowledge retrieval by classification.
2. **Vendor depth gap** — Open WebUI / Hermes / Honcho were not installed as full upstream products; contracts were proven via adapters. A later spike may deepen vendor integration without changing KORA docs.
3. **Council LLM deliberation** not exercised — selection/synthesis rules simulated.

---

## Lessons learned

1. Architecture contracts are implementable as an explicit façade without rewriting Phase 13 docs around tools.
2. Isolation under `/mnt/monarch/prototypes/` works and keeps git clean.
3. Chroma as an isolated index does not require Phase 12 network attachment.
4. Memory candidate staging with forced non-approval successfully prevents silent persistence.
5. Classification-aware retrieval is required before claiming production-quality Context Assembly.

---

## ADR feedback

| ADR | Feedback |
| --- | --- |
| ADR-0004 Hermes | Provisional Adopt remains appropriate; full Hermes install still needs a façade-first spike. No Reject. |
| ADR-0005 Honcho | Spike posture confirmed: approval-gated candidates required; do not Adopt as ungated Memory Runtime. |
| ADR-0006 ChromaDB | Provisional Adopt confirmed for retrieval index role; reinforce non-SoT + classification-scoped queries. |
| ADR-0007 Graphify | Remains Defer / excluded — no change. |
| ADR-0008 Open WebUI | Provisional Adopt confirmed for UI-only identity constraints; full UI install still pending. |

No ADR status changes required solely from 13.11; optional future amendments may add “classification-scoped retrieval” as an adoption constraint on ADR-0006.

---

## Recommendation for production readiness

**Not production-ready.**

Ready for Phase 13.12 planning toward:

- deeper vendor substrate spike (real Open WebUI ↔ façade ↔ Hermes) **still non-production**, and/or
- Context Assembly retrieval gating fixes, and/or
- implementation sequencing / hardening docs

Do **not** migrate Phase 12 AI services or promote this lab to production.

---

## Artifacts

- `Architecture/ai/Runtime_Spike_Execution.md`
- `Validation/Phase13.11/*`
- Lab (outside git): `/mnt/monarch/prototypes/kora-spike/`
