# Phase 13.12 — Context Intelligence Model

**Status:** ✅ Complete (2026-08-01)  
**Scope:** Architecture and specification only (no Docker, runtime implementation, vendor/DB selection)

---

## Objective

Design the intelligence layer between Classification and Context Assembly so KORA selects, filters, ranks, and assembles **only relevant** information—addressing Phase 13.11 naïve keyword over-fetch.

---

## Documents created

| Document | Purpose |
| --- | --- |
| `Architecture/ai/Context_Intelligence.md` | Purpose, responsibilities, boundaries, I/O, subsystem interactions |
| `Architecture/ai/Retrieval_Strategies.md` | Per-class store query/ignore policies |
| `Architecture/ai/Context_Ranking.md` | Ranking axes, budgets, pruning, conflicts |
| `Documentation/Phase13/Context_Intelligence_Model.md` | This report |

---

## Documents updated

| Document | Change |
| --- | --- |
| `Context_Assembly.md` | Upstream Context Intelligence; lifecycle; doc map |
| `Knowledge_Runtime.md` | Classification-driven retrieval expectations; doc map |
| `Memory_Runtime.md` | Strategy-aware retrieval rules; doc map |
| `KORA.md` | References + future evolution |
| `README.md` / `FuturePlans.md` | Index + status |
| `Documentation/Phase13/Phase13_Roadmap.md` / `README.md` | Phase 13.12 |
| `Architecture/standards/StandardsRoadmap.md` | Phase 13.12 |

---

## Architectural decisions

1. **Classification-driven retrieval** — strategy selected by request class.
2. **Selective retrieval** — default is not global search across all stores.
3. **Retrieval budgets** and **context size limits** — conceptual; prune before assembly.
4. **Memory-first / Knowledge-first / Tool-first / Clarification-first** modes by class.
5. **Conflict handling** — surface + authority order; no silent winner.
6. **Confidence propagation** — labels survive into assembly/explainability.
7. **Relationship-aware retrieval** — conceptual; Graphify remains off default path.
8. **Unknown detection** and **missing-information** flags — no fabrication.
9. **Context pruning** after ranking; never drop sole conflict counterpart silently.
10. **Authority ordering** and **freshness weighting** as ranking axes.
11. **Provenance preservation** end-to-end.
12. **Context Intelligence prepares context only** — does not decide; Council remains authoritative.

---

## Retrieval model

Defined in `Retrieval_Strategies.md`: per-class allow/deny for Memory, Knowledge, Tools, Agents; Graphify excluded by default.

Required scenario behaviors:

| Prompt | Behavior |
| --- | --- |
| “I prefer Jellyfin.” | Memory only; no Knowledge |
| “Why did we choose Traefik?” | Knowledge (ADRs/architecture); Memory off by default |
| “What containers are running?” | Tools only |
| “What do you remember about me?” | Memory only |
| “Continue Phase 13.” | Project Memory + project/roadmap/architecture Knowledge |
| “I'm not sure.” | Clarification; minimal retrieval |

---

## Ranking model

Axes: relevance, authority, freshness, confidence, relationship weight, safety.  
Budgets apply after strategy gates (preference Knowledge budget = 0).

---

## Classification model

Classification (existing Selection/classifier) **gates** strategy choice. Ambiguous class → safer/narrower plan or clarification. Re-classification invalidates prior retrieval plan.

---

## Context budget

Per-store soft maxima + final prune for minimum sufficient context. Exact tokens deferred to implementation.

---

## Conflict handling

Dual-cite material Knowledge conflicts; prefer higher authority for ordering; do not drop the lower-authority counterpart from conflict view without noting omission.

---

## Explainability impact

Skip logs (stores ignored), top evidence refs, conflict flags, and confidence posture become part of explainability substrate—without raw CoT.

---

## Findings from Phase 13.11

| Finding | How addressed |
| --- | --- |
| Preference turn over-fetched Knowledge via keyword search | User preference strategy: **Knowledge = No** |
| Need classification-aware retrieval | Context Intelligence between Classification and Assembly |
| Boundaries held but assembly quality weak | Ranking + budgets + pruning specs |

---

## Deferred implementation

Vendor/RAG/embeddings/Docker/API implementation; Graphify; production deployment; deepening Open WebUI/Hermes installs.

---

## Consistency checks

| Requirement | Status |
| --- | --- |
| Separations preserved | ✅ |
| Retrieval ≠ decisions | ✅ |
| No rewrite of 13.0–13.11 contracts | ✅ integration refs only |
| No tech lock-in | ✅ |
| Graphify off default path | ✅ |

---

## Recommendation for next phase (13.13)

Non-production spike **update** to implement classification-aware retrieval gates against `Retrieval_Strategies.md` and re-run Phase 13.11 scenarios (especially preference) to prove Knowledge is not queried—still under `/mnt/monarch/prototypes/kora-spike/`, still no Phase 12 impact.
