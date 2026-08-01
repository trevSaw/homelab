---
title: ADR-0005 Memory Runtime — Honcho
document_type: ADR
service: kora
owner: Homelab
status: Spike
version: 0.2.0
last_reviewed: 2026-08-01
related_documents:
  - Architecture/ai/Memory.md
  - Architecture/ai/Memory_Runtime.md
  - Architecture/ai/Context_Assembly.md
  - Architecture/ai/Implementation_Architecture.md
  - Architecture/decisions/ADR-0004-KORA-Orchestration-Hermes.md
  - Architecture/ai/Technology_Evaluation_ADR_Template.md
---

# ADR-0005 — Memory Runtime (Honcho)

## Meta

| Field | Value |
| --- | --- |
| ADR ID | ADR-0005 |
| Title | Memory Runtime — Honcho |
| Date | 2026-08-01 |
| Author | Homelab |
| Candidate technology | Honcho (Plastic Labs; Hermes memory provider) |
| Proposed implementation layer | Memory Runtime |
| Related architecture docs | `Memory.md`, `Memory_Runtime.md`, `Context_Assembly.md`, ADR-0004 |

## Status

**Spike** — Honcho is a strong *user-modeling* candidate but does not yet demonstrably satisfy the full `Memory_Runtime.md` category/governance model. Time-boxed evaluation only; not adopted as production Memory Runtime.

## Context

KORA requires a Memory Runtime implementing capture → evaluate → classify → store → retrieve → use → review → expire, with categories **User / Project / Operational / Temporary Context**, user correction/deletion, and Memory ≠ Knowledge (`Memory_Runtime.md`).

Honcho is an AI-native memory backend emphasizing dialectic user modeling, peer cards, session context, semantic search, and conclusions. It integrates tightly as a Hermes memory provider. That coupling is both an opportunity (with ADR-0004) and a risk (architecture following the tool).

## Candidate Summary

Honcho provides evolving user representations, session-scoped context injection, search, and conclude/create/delete style operations. Mapped to KORA it would sit in **Memory Runtime**—primarily for **User Memory**—if wrapped with our lifecycle and category rules.

## Architecture Fit

| Criterion | Assessment |
| --- | --- |
| Architecture Fit | **Partial** — excellent user continuity; incomplete category coverage |
| KORA Alignment | **Conditional** — must remain a KORA subsystem, not “Honcho personality” |
| Council Compatibility | **Neutral** — memory feeds Context Assembly; must not vote/decide |
| Memory/Knowledge Boundary | **Risk** — dialectic conclusions can look like Knowledge if unlabeled |
| Security | **Conditional** — cloud vs self-host; secrets exclusion mandatory |
| Governance | **Gap** — auto-dialectic vs confirmation rules in Memory_Runtime |
| Maintenance Burden | **Medium** — another service + provider config |
| Integration Complexity | **Low–medium with Hermes; higher standalone** |
| Migration Risk | **Medium** — provider-shaped profiles/conclusions |
| Performance | **Likely adequate** at homelab scale |
| Community / Project Health | **Active** via Plastic Labs + Hermes integration |
| Operational Complexity | **Medium** |
| Decision | **Spike** |

Evaluate checklist:

- [~] Memory lifecycle — Capture/Evaluate/Classify not fully native; need façade
- [~] Categories — User strong; Project/Operational/Temporary not first-class
- [~] User control — profile/conclude tools help; UX flows still ours
- [x] Provenance — possible if we label Honcho-sourced items in Context Assembly
- [ ] Secrets never stored — policy required, not inherent

**Architecture fit notes:** Honcho optimizes “who is the user?” dialectic memory. KORA Memory Runtime also requires project continuity, operational lessons, and aggressive Temporary Context expiry—those need additional design even if Honcho is used.

**Deal-breakers found:** None absolute for a spike. Soft deal-breaker if dialectic auto-writes durable “facts” without Evaluate/Classify/confirmation gates.

### Specific evaluation questions

| Question | Answer |
| --- | --- |
| Satisfy Memory_Runtime.md? | **Not fully as-is** — needs classification + governance wrapper |
| Distinguish user/project/operational/temporary? | **User + session yes; project/operational/temporary incomplete** |
| Correction/deletion/governance? | **Partial** — conclude delete/update; confirmation UX still required |
| Preserve memory provenance? | **Yes if labeled** in Context Assembly; default may under-label |

## Security

Prefer self-hosted path for spike if available; treat cloud as higher data-boundary risk. Ban secrets in memory content. Multi-peer isolation helps multi-agent scenarios but does not equal KORA permission model.

## Maintenance

Provider upgrades tied to Hermes; document mapping from Honcho artifacts → Memory categories.

## Integration

Natural with Hermes (ADR-0004). Standalone API possible but increases integration work. Must not replace Knowledge Runtime (ADR-0006) or Graphify relationships (ADR-0007).

## Performance

Homelab OK if dialectic cadence is bounded (cost/latency).

## Migration

Export conclusions/profiles before assuming durability. Keep Memory contracts portable.

## Community

Active integration in Hermes docs; stewardship split across Honcho + Hermes ecosystems.

## Operational Complexity

Additional dependency on orchestration spike. Day-2 includes provider health and data export drills.

## Governance

Auto-derived insights require confirmation when ambiguous/sensitive (`Memory_Runtime.md`). Never promote Memory → Knowledge silently.

## Alternatives Considered

| Alternative | Pros | Cons |
| --- | --- | --- |
| Custom Memory Runtime | Exact category/governance fit | Higher build cost |
| Hermes built-in file memory only | Simple | Weak modeling; still not full Runtime |
| Other providers (Mem0-class) | Alternatives | Same category-mapping problem |
| Defer entirely | No coupling | Slows continuity UX |
| Honcho | Strong user modeling + Hermes path | Incomplete Memory_Runtime coverage |

## Decision

**Spike** — time-boxed, non-production evaluation of Honcho as a **User Memory / session continuity** backend candidate under KORA Memory Runtime contracts.

**Decision statement:** Do not adopt Honcho as the complete Memory Runtime. Validate whether it can serve User Memory (and possibly session Temporary Context) behind Evaluate/Classify/provenance gates during the Hermes orchestration spike.

**Constraints / conditions:**

1. Memory ≠ Knowledge enforced in Context Assembly labeling.
2. No automatic durable writes for sensitive/inferred items without confirmation policy.
3. Project/Operational Memory remain explicitly designed—even if temporarily stubbed.
4. No production deployment; no Phase 12 changes.
5. Spike exit criteria: map Honcho artifacts → Memory categories; prove correct/delete; prove non-promotion to Knowledge.

**Rollback plan:** Disable provider; discard spike data; retain architecture. Choose custom Memory Runtime later without rewriting KORA.md.

## Consequences

**Positive:** Fast path to deep user continuity alongside Hermes; deletion/search primitives exist.

**Negative:** Category model mismatch; dialectic may over-infer; Hermes coupling increases.

## Implementation Notes

Spike only after ADR-0004 façade rules are drafted. No compose/install authorized by this ADR alone.
