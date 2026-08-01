---
title: ADR-0006 Knowledge Retrieval — ChromaDB
document_type: ADR
service: kora
owner: Homelab
status: Provisional Adopt
version: 0.2.0
last_reviewed: 2026-08-01
related_documents:
  - Architecture/ai/Knowledge.md
  - Architecture/ai/Knowledge_Runtime.md
  - Architecture/ai/Context_Assembly.md
  - Architecture/ai/Implementation_Architecture.md
  - Architecture/ai/Technology_Evaluation_ADR_Template.md
---

# ADR-0006 — Knowledge Retrieval (ChromaDB)

## Meta

| Field | Value |
| --- | --- |
| ADR ID | ADR-0006 |
| Title | Knowledge Retrieval — ChromaDB |
| Date | 2026-08-01 |
| Author | Homelab |
| Candidate technology | ChromaDB |
| Proposed implementation layer | Knowledge Runtime (retrieval store) |
| Related architecture docs | `Knowledge.md`, `Knowledge_Runtime.md`, `Context_Assembly.md` |

## Status

**Provisional Adopt** — ChromaDB is accepted as the preferred **semantic retrieval substrate candidate** for Knowledge Runtime. It stores/retrieves embeddings and metadata; it is **not** the knowledge authority. Repository documents/ADRs remain SoT.

## Context

KORA Knowledge Runtime needs indexing/retrieval with authority, freshness, provenance, confidence, and supersession awareness (`Knowledge_Runtime.md`). Phase 13.2/13.5 forbid treating chat, live tools, or a vector DB as automatic Authoritative Knowledge.

ChromaDB is a widely used embedding database suitable for homelab-scale RAG retrieval. Evaluation asks whether it can implement *retrieval*, not whether it should become the corpus of record.

## Candidate Summary

ChromaDB provides collections, embeddings, metadata filters, and query APIs. In KORA it occupies **Knowledge Runtime retrieval**—an index over governed sources—not the promotion pipeline or authority tier registry.

## Architecture Fit

| Criterion | Assessment |
| --- | --- |
| Architecture Fit | **Pass (retrieval only)** |
| KORA Alignment | **Pass** if metadata carries provenance/authority/freshness |
| Council Compatibility | **Pass** — retrieval feeds Context Assembly; does not decide |
| Memory/Knowledge Boundary | **Pass** if Memory is never silently indexed as Knowledge |
| Security | **Conditional** — local store preferred; no secrets in collections |
| Governance | **External** — promotion stays in repo/ADR process |
| Maintenance Burden | **Low–medium** |
| Integration Complexity | **Low–medium** |
| Migration Risk | **Medium** — embeddings not portable 1:1 across models |
| Performance | **Good** for homelab corpus sizes |
| Community / Project Health | **Strong** open-source ecosystem |
| Operational Complexity | **Low–medium** |
| Decision | **Provisionally Adopt** |

Evaluate checklist:

- [x] Retrieval capability — strong
- [~] Provenance — via metadata we define; not automatic wisdom
- [~] Authority/freshness — must be our metadata + filters
- [x] Context Assembly integration — standard RAG pattern
- [x] Limitations acknowledged — not SoT; weak native supersession graph

**Architecture fit notes:** ChromaDB satisfies the *store/retrieve* portion of Knowledge Runtime. Validation/promotion/authority remain KORA/repo governance.

**Deal-breakers found:** None for provisional retrieval adoption. Deal-breaker would be treating Chroma as authoritative without provenance.

### Specific evaluation questions

| Question | Answer |
| --- | --- |
| Satisfy Knowledge_Runtime.md? | **Partially by design** — retrieval yes; promotion/authority no (correct split) |
| Retrieval capability? | **Yes** |
| Provenance support? | **Yes via metadata contract** we own |
| Authority/freshness handling? | **Yes if indexed fields + filters**; not built-in governance |
| Context assembly integration? | **Yes** |
| Limitations? | Embedding model lock-in; not a relationship graph; not SoT |

## Security

Local/self-hosted preference. Exclude secrets. Access control at service boundary when deployed later. Index only approved sources.

## Maintenance

Reindex on embedding model change. Backup collections + source mapping. Keep ingestion scripts simple and auditable.

## Integration

Pairs with Context Assembly; complements Graphiti (ADR-0007) for relationships. Must not ingest Memory stores as Knowledge by default.

## Performance

Adequate for documentation-scale corpora. Latency dominated by embedding/model calls, not Chroma itself at this scale.

## Migration

Export IDs + source URIs + metadata; rebuild embeddings if model changes. Source documents remain in git.

## Community

Mature open-source project; broad tooling support.

## Operational Complexity

Single retrieval service pattern; watch disk growth and reindex jobs.

## Governance

Chroma never outranks ADRs/standards. Candidate → Validated → Authoritative promotion remains outside the DB.

## Alternatives Considered

| Alternative | Pros | Cons |
| --- | --- | --- |
| Repo-only retrieval | Perfect SoT alignment | Weak semantic recall |
| Other vector DBs | Similar capability | Similar metadata burden |
| Defer retrieval | Less ops | Slower Knowledge UX |
| ChromaDB | Simple, common, self-hostable | Metadata discipline required |

## Decision

**Provisionally Adopt** ChromaDB as the Knowledge Runtime **retrieval index candidate**.

**Decision statement:** Use ChromaDB (when implementation begins) to index governed knowledge sources for semantic retrieval. Repository documents and ADRs remain authoritative. Chroma stores/retrieves; it does not decide truth.

**Constraints / conditions:**

1. Mandatory metadata: source URI, authority tier, freshness/updated_at, provenance, supersession pointers where known.
2. No silent Memory/Tool → Knowledge indexing.
3. No production claim that “it’s in Chroma, therefore true.”
4. No install authorized by this ADR alone.

**Rollback plan:** Drop collections; continue repo-based retrieval. Re-point Knowledge Runtime to another index without rewriting Knowledge.md.

## Consequences

**Positive:** Practical RAG path; low conceptual conflict if SoT boundary held.

**Negative:** Teams may over-trust retrieval snippets; embedding churn; metadata discipline is mandatory work.

## Implementation Notes

Next implementation phase may prototype ingestion from Architecture/Documentation/Services—not in Phase 13.8. No Docker/compose here.
