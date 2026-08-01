---
title: ADR-0007 Relationship Layer — Graphiti
document_type: ADR
service: kora
owner: Homelab
status: Defer
version: 0.2.0
last_reviewed: 2026-08-01
related_documents:
  - Architecture/ai/Knowledge.md
  - Architecture/ai/Knowledge_Runtime.md
  - Architecture/ai/Implementation_Architecture.md
  - Architecture/decisions/ADR-0006-Knowledge-Retrieval-ChromaDB.md
  - Architecture/ai/Technology_Evaluation_ADR_Template.md
---

# ADR-0007 — Relationship Layer (Graphiti)

## Meta

| Field | Value |
| --- | --- |
| ADR ID | ADR-0007 |
| Title | Relationship Layer — Graphiti |
| Date | 2026-08-01 |
| Author | Homelab |
| Candidate technology | Graphiti (getzep/graphiti) |
| Proposed implementation layer | Relationship Knowledge |
| Related architecture docs | `Knowledge.md`, `Knowledge_Runtime.md`, `Implementation_Architecture.md`, ADR-0006 |

## Status

**Defer** — Graphiti is a strong fit for temporal relationship modeling and complements ChromaDB retrieval, but adds graph DB operational complexity before a thin vertical slice exists. Revisit after orchestration + retrieval paths are proven. (Earlier informal name “Graphfy” is superseded by **Graphiti**.)

## Context

KORA Knowledge Architecture requires conceptual relationships among projects, services, decisions, documents, dependencies, and historical change—without making a graph the sole SoT. Phase 13.7 listed a Relationship Knowledge layer as optional/complementary.

**Graphiti** (Zep) builds temporal context graphs with bi-temporal facts, episode provenance, invalidation without deletion, and hybrid search. That matches relationship + historical needs better than a pure vector store.

## Candidate Summary

Graphiti maintains evolving entities/edges with validity windows and provenance to source episodes. In KORA it would occupy **Relationship Knowledge**—linking governed documents and infrastructure concepts—while ChromaDB (ADR-0006) handles semantic chunk retrieval.

## Architecture Fit

| Criterion | Assessment |
| --- | --- |
| Architecture Fit | **Strong conceptual fit; deferred for sequencing** |
| KORA Alignment | **Pass if graph ≠ authority** |
| Council Compatibility | **Pass** — relationships inform Context Assembly |
| Memory/Knowledge Boundary | **Risk** — Graphiti is often framed as agent memory; must stay Knowledge relationships, not Memory Runtime |
| Security | **Conditional** — graph store + extraction model access |
| Governance | **External** — edges derived from governed sources |
| Maintenance Burden | **High** relative to early phase needs |
| Integration Complexity | **Medium–high** (graph DB dependency typically Neo4j-class) |
| Migration Risk | **Medium** |
| Performance | **Good when tuned**; extraction cost non-trivial |
| Community / Project Health | **Active** (getzep/graphiti) |
| Operational Complexity | **High for first slice** |
| Decision | **Defer** |

Evaluate checklist:

- [x] Relationship modeling needs — strong
- [x] Projects/services/decisions/documents/dependencies/history — representable
- [x] Complements Knowledge Runtime / Chroma — yes (graph vs vector)
- [x] Unnecessary complexity *now* — yes for pre-slice phase

**Architecture fit notes:** Excellent long-term complement. Premature as a blocking dependency before UI→orchestration→retrieval thin slice.

**Deal-breakers found:** None. Soft deal-breaker if adopted as Memory Runtime substitute or document SoT.

### Specific evaluation questions

| Question | Answer |
| --- | --- |
| Satisfy relationship modeling? | **Yes (promising)** |
| Represent projects/services/decisions/docs/deps/history? | **Yes via entities/edges + temporal validity** |
| Complement Knowledge Runtime? | **Yes** alongside Chroma retrieval |
| Unnecessary complexity? | **Yes at this sequencing stage** |

## Security

When revisited: local graph store, controlled ingestion, no secrets in episodes, least-privilege model access for extraction.

## Maintenance

Ontology drift, re-extraction, graph backups, version pins. Higher than Chroma alone.

## Integration

Should read from the same governed sources as Chroma ingestion. Must not replace ADR/document authority. Must not absorb Honcho/user Memory.

## Performance

Hybrid retrieval is attractive; LLM extraction for graph construction is the cost center.

## Migration

Export graph snapshots; retain source documents as rebuild substrate.

## Community

Active open-source project with commercial sibling (Zep). Prefer OSS Graphiti path for self-host evaluation later.

## Operational Complexity

Primary reason to defer: graph infrastructure + extraction pipeline before KORA vertical slice exists.

## Governance

Derived edges are Candidate Knowledge until validated. Point-in-time queries support LUMA-style historical reasoning without erasing supersession.

## Alternatives Considered

| Alternative | Pros | Cons |
| --- | --- | --- |
| Manual markdown/link indexes | Simple | Weak temporal/query power |
| Defer (chosen) | Reduces early ops load | Delays rich project awareness UX |
| Other graph DBs | Flexible | Still high ops; less temporal agent focus |
| Adopt Graphiti now | Best relationship fit | Complexity before thin slice |

## Decision

**Defer** Graphiti adoption until after provisional Hermes façade + Chroma retrieval paths are demonstrated in a thin slice.

**Decision statement:** Graphiti remains the preferred **relationship-layer candidate** on Architecture Fit, but is not provisionally adopted for implementation sequencing reasons. Re-open this ADR when Knowledge retrieval ingestion exists and project-awareness UX is prioritized.

**Constraints / conditions:**

1. Do not implement Graphiti in Phase 13.8.
2. Do not substitute Graphiti for Memory Runtime (ADR-0005) or document SoT.
3. When reopened, require provenance-to-source and non-authority constraints equal to ADR-0006.

**Rollback plan:** N/A (not adopted). If a future spike fails, fall back to manual relationship indexes + Chroma.

## Consequences

**Positive:** Avoids early operational drag; keeps candidate clearly evaluated.

**Negative:** Project/dependency awareness UX stays document/retrieval-limited longer.

## Implementation Notes

No install. Update Implementation_Architecture candidate naming from informal “Graphfy” to Graphiti in a later doc pass if needed; this ADR is authoritative for the candidate identity.
