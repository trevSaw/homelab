# KORA Context Ranking

**Status:** Canonical conceptual specification (Phase 13.12)  
**Platform:** KORA / Brainiac (`KORA.md`)  
**Companions:** `Context_Intelligence.md`, `Retrieval_Strategies.md`, `Context_Assembly.md`

Defines how KORA decides **what belongs in the context window** after selective retrieval and before Context Assembly.

No tokenizers, vendors, or embedding algorithms selected here.

---

## Purpose

Rank, budget, and prune candidate evidence so Council receives **minimum sufficient, provenance-labeled** context—not an unfiltered corpus dump.

---

## Ranking Model (Conceptual Axes)

Each candidate is scored along:

| Axis | Meaning |
| --- | --- |
| **Relevance** | Fit to classified request and user constraints |
| **Authority** | Knowledge tier (Authoritative > Validated > Candidate > informal) |
| **Freshness** | Recency / valid-as-of; critical for Tools |
| **Confidence** | Memory confidence or Knowledge certainty cues |
| **Relationship weight** | Conceptual link strength to the request topic (Graphify deferred—use doc links/metadata when present) |
| **Safety** | Hard filter: secrets/forbidden content score as exclude |

Ranking **orders within an allowed store**. It must not promote Memory above Knowledge authority for standards questions, nor Knowledge above Tools for live state.

---

## Authority Ordering

For Knowledge candidates:

1. Approved ADR / Standard / Phase baseline  
2. Validated service/architecture docs  
3. Working drafts / candidates  
4. Informal notes  

Informal notes may be retrieved for **conflict scenarios** but must not outrank ADRs in synthesis guidance.

---

## Freshness Weighting

| Class | Freshness rule |
| --- | --- |
| Tools | Prefer newest evidence; stale live claims → downrank or drop |
| Memory | Prefer newer explicit corrections over older statements |
| Knowledge | Prefer non-superseded; keep historical only when asked |
| Conversation | Short-lived Temporary Context; low authority |

---

## Relevance

- Classification strategy already limited stores; relevance ranks **within** those results
- Preference strategies: Knowledge relevance is N/A (Knowledge not queried)
- Keyword-only relevance is insufficient architecturally—implementation must respect strategy gates first (Phase 13.11 lesson)

---

## Relationship Weighting

Conceptual only:

- Prefer candidates linked to the active project/phase/service named in the request
- Do not require Graphify; use explicit metadata/paths when available
- Relationship weight never overrides authority for policy questions

---

## Confidence Propagation

- Carry confidence/authority into Context Assembly and Explainability
- Low-confidence Memory stays labeled low; does not become high via proximity to Knowledge
- Missing tool evidence → confidence **unknown**, not invented high confidence

---

## Conflict Handling

| Situation | Ranking behavior |
| --- | --- |
| Knowledge vs Knowledge | Keep both sides if material; mark conflict; prefer higher authority for default ordering but **do not drop** the loser from conflict view |
| Memory vs Knowledge | Both may appear if strategy allowed both; labels stay separate; Memory does not override ADR authority |
| Tool vs Knowledge | Surface both; likely freshness; do not silent-pick |
| Preference vs Knowledge | Preference strategy should not have queried Knowledge |

Silent single-winner collapse is a defect.

---

## Retrieval Budget

Conceptual budgets (implementation may tune numbers):

| Store | Default soft max candidates into ranking |
| --- | --- |
| Memory | Small (e.g. handful of preference/project items) |
| Knowledge | Modest set of top-relevant docs/sections |
| Tools | Only calls needed for the asked live facts |
| Agents | Only returned results for the open gap |

**Hard rule:** Budgets apply **after** strategy gating. A preference turn’s Knowledge budget is **zero**.

---

## Context Size Limits

Assembly receives a pruned set aiming for minimum sufficient context:

1. Safety exclusions  
2. Strategy allow-list  
3. Rank within store  
4. Apply per-store budget  
5. Cross-store merge without laundering  
6. Final prune if still oversized (drop lowest relevance first; never drop sole conflict counterpart without noting omission)

Exact token limits are implementation concerns.

---

## Context Pruning

Prune when:

- Duplicate provenance (same source repeated)
- Off-strategy leakage (should not occur if gates hold)
- Deprecated Knowledge unless historical question
- Low-relevance tail beyond budget
- Secret-bearing or user-forbidden content

Do **not** prune:

- The only evidence supporting a material claim
- Conflict counterparts needed for honesty
- User corrections that supersede older Memory

---

## Unknown Detection & Missing Information

| Signal | Action |
| --- | --- |
| Strategy requires Tools; Tools unavailable | Flag missing live evidence; do not fabricate |
| Strategy requires Knowledge; zero hits | Flag gap; ask for pointer or broaden **once** under budget |
| Classification = unknown/clarification | Skip heavy retrieval; ask clarifying question |
| User says “I'm not sure.” | Clarification-first; minimal context |

---

## What Belongs in the Context Window?

Include a candidate if **all** hold:

1. Allowed by active retrieval strategy  
2. Passes safety filter  
3. Has provenance labels  
4. Survives ranking vs budget  
5. Adds non-duplicate signal for the classified ask  

Otherwise exclude—and record skip/prune reason when material for explainability.

---

## Explainability Impact

Ranking/skips should be summarizable as:

- which stores were queried/ignored  
- top evidence refs  
- conflicts retained  
- confidence posture  

No raw chain-of-thought required or allowed.

---

## Document Map

| Document | Role |
| --- | --- |
| `Context_Ranking.md` (this file) | Score, budget, prune, conflicts |
| `Context_Intelligence.md` | Owns when ranking runs |
| `Retrieval_Strategies.md` | What may be ranked at all |
| `Context_Assembly.md` | Consumes pruned ranked set |
