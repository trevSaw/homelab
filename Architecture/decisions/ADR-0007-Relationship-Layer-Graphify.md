---
title: ADR-0007 Relationship Layer — Graphify
document_type: ADR
service: kora
owner: Homelab
status: Accepted for Future Implementation
version: 0.4.0
last_reviewed: 2026-08-06
related_documents:
  - Architecture/ai/Knowledge.md
  - Architecture/ai/Knowledge_Runtime.md
  - Architecture/ai/Implementation_Architecture.md
  - Architecture/decisions/ADR-0006-Knowledge-Retrieval-ChromaDB.md
  - Architecture/ai/Technology_Evaluation_ADR_Template.md
  - Services/ServiceIndex.md
  - Documentation/Phase14/Phase14_Roadmap.md
---

# ADR-0007 — Relationship Layer (Graphify)

## Meta

| Field | Value |
| --- | --- |
| ADR ID | ADR-0007 |
| Title | Relationship Layer — Graphify |
| Date | 2026-08-01 |
| Author | Homelab |
| Candidate technology | Graphify ([Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify)) |
| Proposed implementation layer | Relationship Knowledge |
| Related architecture docs | `Knowledge.md`, `Knowledge_Runtime.md`, `Implementation_Architecture.md`, ADR-0006 |

## Status

**Accepted for Future Implementation (Target: Phase 14.4 — Knowledge Graph)** — Graphify is an intentional architectural component. It is scheduled for Phase 14.4 and has **not** yet been implemented. It remains behind the implementation gate until that phase begins. Prior mis-identification as “Graphiti” is void.

## Context

KORA Knowledge Architecture requires conceptual relationships among projects, services, decisions, documents, dependencies, and historical change—without making a graph the sole SoT. Phase 13.7 listed a Relationship Knowledge layer as optional/complementary.

**Graphify** turns codebases, docs, SQL schemas, configs, and PDFs into a queryable knowledge graph via local deterministic AST parsing, with explained edges and **no vector store**. It is exposed as a `/graphify` skill for Claude Code, Cursor, Codex, and Gemini CLI. That profile matches “relationship modeling over the homelab repo/docs” more closely than a temporal agent-memory graph product.

## Candidate Summary

Graphify builds structural/relationship graphs from local sources with explainable edges. In KORA it would occupy **Relationship Knowledge**—linking governed documents and infrastructure concepts—while ChromaDB (ADR-0006) handles semantic chunk retrieval. Graphify must not become document authority or Memory Runtime.

## Architecture Fit

| Criterion | Assessment |
| --- | --- |
| Architecture Fit | **Strong for repo/docs relationship extraction; runtime packaging TBD** |
| KORA Alignment | **Pass if graph ≠ authority and ≠ product identity** |
| Council Compatibility | **Pass** — relationships inform Context Assembly; do not decide |
| Memory/Knowledge Boundary | **Pass if scoped** — structural Knowledge relationships, not User Memory |
| Security | **Favorable locally** — local parse; still gate which trees/PDFs are ingested |
| Governance | **External** — edges derived from governed sources; explainable edges help audit |
| Maintenance Burden | **Low–medium** if skill/local; higher if operated as always-on service |
| Integration Complexity | **Medium** — skill-oriented packaging may not map 1:1 to KORA runtime |
| Migration Risk | **Low–medium** — rebuildable from sources if SoT remains git |
| Performance | **Likely adequate** for homelab corpus; AST path avoids embedding cost |
| Community / Project Health | **Active / high visibility** (Graphify-Labs/graphify) |
| Operational Complexity | **Lower than heavy graph-DB stacks**; still deferred for sequencing |
| Decision | **Accepted for Future Implementation (Phase 14.4)** |

Evaluate checklist:

- [x] Relationship modeling needs — strong for code/docs/schemas
- [~] Projects/services/decisions/documents/dependencies/history — representable from sources; history depth depends on how Graphify models change over time
- [x] Complements Knowledge Runtime / Chroma — yes (structural graph vs semantic vectors; Graphify explicitly no vector store)
- [x] Unnecessary complexity *now* — yes before thin slice; also packaging validation needed

**Architecture fit notes:** Excellent conceptual match for “queryable relationships over the repo.” Main open question is whether Graphify runs as a durable KORA Relationship Knowledge service or remains an external analysis skill feeding ingestion.

**Deal-breakers found:** None. Soft deal-breaker if Graphify output is treated as SoT or if it silently becomes Memory.

### Specific evaluation questions

| Question | Answer |
| --- | --- |
| Satisfy relationship modeling? | **Yes (promising)** for codebase/docs graphs |
| Represent projects/services/decisions/docs/deps/history? | **Likely for structural/current links**; historical supersession may still need ADR/doc process |
| Complement Knowledge Runtime? | **Yes** alongside Chroma retrieval (orthogonal: graph vs vectors) |
| Unnecessary complexity? | **Moderate** — lighter than graph-DB platforms, but still premature before thin slice |

## Security

Local parsing is attractive. Constrain input paths; exclude secrets/credentials; do not ingest private appdata. When later integrated with KORA, expose graph query behind orchestration—not raw filesystem tools by default.

## Maintenance

Regenerate graph when sources change. Prefer rebuild-from-git over hand-edited edges. Pin skill/tool versions if used in automation.

## Integration

Should read the same governed sources as Chroma ingestion. Explained edges support Explainability. Must not replace ADR/document authority. Must not absorb Honcho/user Memory.

## Performance

Deterministic AST/local parse avoids embedding pipelines for relationship extraction. Query latency depends on resulting graph size—homelab-scale expected OK.

## Migration

Sources remain in git. Graph artifacts are disposable indexes. Exit cost is low if rebuildable.

## Community

Graphify-Labs/graphify — high visibility; evaluate stewardship and release discipline before production reliance.

## Operational Complexity

Lower than Neo4j-class temporal graph stacks. Remaining complexity is packaging (skill vs service) and keeping graph fresh with repo changes. Primary scheduling reason: sequenced after the Knowledge Platform (Phase 14.3) plus runtime-fit validation, not inherent platform weight alone.

## Governance

Derived edges are Candidate Knowledge until validated. Graphify explanations help audit but do not replace human/ADR authority.

## Alternatives Considered

| Alternative | Pros | Cons |
| --- | --- | --- |
| Manual markdown/link indexes | Simple | Weak query power |
| Schedule for Phase 14.4 (chosen) | Intentional component; thin slice first; validate runtime packaging | Delays rich relationship UX until Knowledge Platform lands |
| Other graph platforms | Flexible | Heavier ops; not the intended candidate |
| Adopt Graphify now | Best named fit for repo→graph | Premature; skill≠runtime unproven |

## Decision

**Accepted for Future Implementation (Target: Phase 14.4 — Knowledge Graph).** Graphify adoption remains gated: it is not implemented in the current phase, and the architectural decision is unchanged. Implementation is scheduled for Phase 14.4 after the Knowledge Platform (ingestion, embeddings, ChromaDB retrieval) is in place, and after Graphify’s skill-vs-runtime packaging is validated for KORA.

**Decision statement:** Graphify ([Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify)) is the preferred **relationship-layer candidate**. It is an intentional architectural component scheduled for Phase 14.4 (Knowledge Graph). It has not yet been implemented and remains behind the implementation gate until that phase. Re-open this ADR before implementation when Knowledge Platform ingestion exists and project-awareness UX is prioritized.

**Constraints / conditions:**

1. Do not implement Graphify before Phase 14.4.
2. Do not substitute Graphify for Memory Runtime (ADR-0005) or document SoT.
3. Do not confuse Graphify with unrelated “Graphiti” / Zep products.
4. At Phase 14.4 implementation, require provenance-to-source and non-authority constraints equal to ADR-0006.
5. Graphify and ChromaDB coexist: Graphify provides relationship modeling and visualization; ChromaDB provides vector indexing and retrieval. Both are infrastructure owned by the Knowledge Service, not peer services.

**Rollback plan:** N/A (not implemented). If a Phase 14.4 spike fails, fall back to manual relationship indexes + Chroma.

## Consequences

**Positive:** Correct candidate identity; lighter relationship path than mis-evaluated alternatives; rebuildable from git.

**Negative:** Project/dependency awareness UX stays limited longer; packaging uncertainty remains.

## Implementation Notes

No install. `Services/ServiceIndex.md` already lists Graphify as researching. This ADR is authoritative for the Graphify candidate identity and its Phase 14.4 scheduling. Graphify is not implemented in the current phase.
