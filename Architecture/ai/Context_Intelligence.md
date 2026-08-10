# KORA Context Intelligence Architecture

**Status:** Canonical architecture specification (Phase 13.12)  
**Platform:** KORA / Brainiac (`KORA.md`)  
**Companions:** `Retrieval_Strategies.md`, `Context_Ranking.md`, `Context_Assembly.md`  
**Placement:** Between **Classification** and **Context Assembly**

Context Intelligence determines **what to retrieve and what to ignore** before assembly.  
It does **not** decide recommendations. Council reasons; KORA synthesizes.

This phase is architecture only—no vendors, embeddings, Docker, or runtime installs.

---

## Purpose

Solve classification-aware context retrieval so KORA does not search every substrate for every request.

Phase 13.11 finding: naïve keyword retrieval over-fetched unrelated Knowledge during a preference turn. Context Intelligence is the architectural response: **selective retrieval driven by classification**, with budgets, ranking, and pruning before Context Assembly.

---

## Placement in the Vertical Slice

```text
User Request
    ↓
Classification          ← Council/Selection request class
    ↓
Context Intelligence    ← THIS DOCUMENT (select / filter / rank plan)
    ↓
Retrieval (selective)   ← Memory / Knowledge / Tools / Agents as allowed
    ↓
Context Ranking         ← score, prune, budget
    ↓
Context Assembly        ← provenance-labeled package
    ↓
Council Deliberation
```

Lifecycle note: `Context_Assembly.md` previously showed Classification → Assembly. Context Intelligence is the explicit step that makes assembly **classification-aware**.

---

## Responsibilities

Context Intelligence **does**:

1. Consume classification (+ optional project/session hints)
2. Choose a **retrieval strategy** (`Retrieval_Strategies.md`)
3. Declare which stores to query vs ignore
4. Set retrieval budgets and priority order
5. Invoke allowed store read-paths (conceptual)
6. Apply ranking/pruning (`Context_Ranking.md`)
7. Hand a ranked candidate set to Context Assembly
8. Preserve provenance and class labels throughout
9. Detect unknown / missing-information situations early
10. Record why stores were skipped (for explainability)

Context Intelligence **does not**:

- Make final recommendations
- Replace Council deliberation
- Promote Memory → Knowledge or Tools → Knowledge
- Execute Administrative/Execute tools
- Rewrite architecture to fit a search vendor
- Query Graphify on the default path (Graphify planned for Phase 14.4; not implemented)

---

## Boundaries

| Boundary | Rule |
| --- | --- |
| Memory ≠ Knowledge | Separate query plans; never merge unlabeled |
| Knowledge ≠ Tools | Live state uses Tools strategy, not Knowledge corpus |
| Tools ≠ Decisions | Retrieved tool evidence informs; does not decide |
| Council ≠ Agents | Intelligence prepares context; agents are not seats |
| Retrieval ≠ Decision | Selecting documents ≠ choosing the user’s path |
| Assembly ≠ Intelligence | Intelligence plans/filters; Assembly packages for deliberation |
| KORA orchestrates | Context Intelligence is a KORA conductor concern |

---

## Inputs

| Input | Source | Required |
| --- | --- | --- |
| User request | UI / conversation | Yes |
| Classification | `Council/Selection.md` / KORA classifier | Yes |
| Conversation Temporary Context | session | Minimal |
| Project / phase hints | session or user | Optional |
| Safety / sensitivity flags | governance | Yes when present |
| Prior assembly gap flags | mid-session expand | Optional |

---

## Outputs

| Output | Consumer |
| --- | --- |
| Retrieval plan (stores on/off, priorities, budgets) | Retrieval executors |
| Ranked evidence candidates (still labeled) | Context Assembly |
| Skip log (why Knowledge/Memory/Tools not queried) | Explainability |
| Unknown / missing-info flags | KORA synthesis / UX |
| Conflict flags (multi-authority Knowledge) | Assembly + Council |

Every candidate retains: `source_class`, `source_ref`, authority/confidence, freshness, retrieval_reason.

---

## Interaction with Classification

Classification **gates** strategy selection.

| Principle | Meaning |
| --- | --- |
| Classification-driven retrieval | Strategy chosen from request class—not global search |
| Selective retrieval | Default is **not** “query everything” |
| Re-classify may re-plan | If class changes mid-session, invalidate prior plan |
| Prefer safer/narrower plan when uncertain | Ambiguous class → clarification or minimal retrieval |

Classification does not retrieve; it selects the strategy Context Intelligence executes.

---

## Interaction with Context Assembly

| Context Intelligence | Context Assembly |
| --- | --- |
| Decides what is eligible | Builds final reasoning package |
| Ranks and prunes candidates | Applies assembly priority + conflict surfacing |
| Supplies skip/conflict flags | Preserves labels for Council/Explainability |

Assembly must not re-open ignored stores unless KORA explicitly requests expansion.

---

## Interaction with Memory

- Queried only when strategy allows (preference, personal, project continuity, …)
- Read path only unless separate Memory governance authorizes writes (out of Intelligence scope)
- Empty Memory is valid
- Never labeled as Knowledge

---

## Interaction with Knowledge

- Queried only when strategy allows (architecture, ADR, research, project knowledge, …)
- Index ≠ SoT; authority from governed sources
- Conflict pairs preserved for ranking/Council
- Graphify not on default path

---

## Interaction with Tools

- Queried only for live/operational/status classes
- Evidence is point-in-time; not Knowledge
- Execute/Administrative still require approval UX outside Intelligence
- Unknown live questions without tools → missing-info flag, no fabrication

---

## Interaction with Council

- Council receives assembled context, not raw unranked dumps
- Intelligence may bias **which evidence** is available; it does not vote
- Disagreement among Knowledge sources is preserved for Council (IRIS/LUMA/NOMA as relevant)
- Member selection remains Selection.md’s job (may run in parallel with Intelligence)

---

## Architectural Decisions (Summary)

Defined fully across this file + `Retrieval_Strategies.md` + `Context_Ranking.md`:

1. **Classification-driven retrieval**
2. **Selective retrieval** (not global)
3. **Retrieval budgets** and **context size limits**
4. **Memory-first / Knowledge-first / Tool-first** situations by class
5. **Conflict resolution** = surface + authority order, not silent pick
6. **Confidence propagation** into assembly/explainability
7. **Relationship-aware retrieval** conceptual (Graphify planned for Phase 14.4)
8. **Unknown detection** and **missing-information handling**
9. **Context pruning** after ranking
10. **Authority ordering** and **freshness weighting**
11. **Provenance preservation** end-to-end

---

## Non-goals

Vendor selection, embeddings, vector search implementation, RAG frameworks, Docker, APIs, production deployment.

---

## Document Map

| Document | Role |
| --- | --- |
| `Context_Intelligence.md` (this file) | Select/filter/rank plan between Classification and Assembly |
| `Retrieval_Strategies.md` | Per-class store policies |
| `Context_Ranking.md` | Ranking, budgets, pruning, conflicts |
| `Context_Assembly.md` | Final package for Council |
| `Documentation/Phase13/Context_Intelligence_Model.md` | Phase 13.12 report |
