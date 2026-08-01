---
title: ADR-0008 User Interface — Open WebUI
document_type: ADR
service: kora
owner: Homelab
status: Provisional Adopt
version: 0.2.0
last_reviewed: 2026-08-01
related_documents:
  - Architecture/ai/User_Experience.md
  - Architecture/ai/Interaction_Model.md
  - Architecture/ai/Explainability.md
  - Architecture/ai/Implementation_Architecture.md
  - Architecture/decisions/ADR-0004-KORA-Orchestration-Hermes.md
  - Architecture/ai/Technology_Evaluation_ADR_Template.md
---

# ADR-0008 — User Interface (Open WebUI)

## Meta

| Field | Value |
| --- | --- |
| ADR ID | ADR-0008 |
| Title | User Interface — Open WebUI |
| Date | 2026-08-01 |
| Author | Homelab |
| Candidate technology | Open WebUI |
| Proposed implementation layer | User Interface |
| Related architecture docs | `User_Experience.md`, `Interaction_Model.md`, `Explainability.md`, ADR-0004 |

## Status

**Provisional Adopt** — Open WebUI is accepted as the preferred **UI layer candidate** only. It is an interaction surface for KORA. It is **not** KORA, not the Council, and not the orchestration brain.

## Context

KORA UX requires chat (and future surfaces), Council visibility modes, explainability without raw chain-of-thought, memory controls, and approval flows (`User_Experience.md`, `Explainability.md`). Phase 13.7 requires UI to integrate with orchestration rather than replace it.

Open WebUI is a popular self-hosted chat UI for local/remote models with extensions, RAG features, and API connectivity. Evaluation focuses on whether it can be *branded and wired* as KORA’s window—not whether its built-in agent/RAG features should redefine architecture.

## Candidate Summary

Open WebUI provides a mature chat UX, user auth options, and extensibility. In KORA it occupies the **User Interface Layer**, fronting the KORA orchestration façade (Hermes substrate per ADR-0004 when spiked).

## Architecture Fit

| Criterion | Assessment |
| --- | --- |
| Architecture Fit | **Conditional pass** — UI yes; disable/ignore competing “brain” features |
| KORA Alignment | **Risk managed by branding + backend routing** |
| Council Compatibility | **Gap** — Council modes need extension/custom panels |
| Memory/Knowledge Boundary | **Risk** — built-in RAG/memory features must not bypass runtimes |
| Security | **Conditional** — auth, network, no host exposure per Phase 12 norms later |
| Governance | **Gap** — approval UX must be added/integrated |
| Maintenance Burden | **Medium** |
| Integration Complexity | **Medium** — must target orchestration API, not raw model-only path long-term |
| Migration Risk | **Low–medium** — UI is replaceable if façade is stable |
| Performance | **Adequate** |
| Community / Project Health | **Strong** |
| Operational Complexity | **Medium** |
| Decision | **Provisionally Adopt** |

Evaluate checklist:

- [x] Interaction surface — strong chat baseline
- [~] KORA identity — achievable with naming/theming; discipline required
- [~] Explainability — needs custom presentation; no raw CoT dump
- [~] Hermes/orchestration connect — via API/façade, not “Open WebUI agents”
- [~] Future project/task/memory visibility — extensible, not native KORA-complete

**Architecture fit notes:** Good first UI. Dangerous if its pipelines become a second orchestration stack.

**Deal-breakers found:** None if constrained. Soft deal-breaker if Open WebUI’s assistant identity replaces KORA or if its RAG becomes Knowledge SoT.

### Specific evaluation questions

| Question | Answer |
| --- | --- |
| Serve as interaction surface? | **Yes** |
| Expose KORA identity rather than replace it? | **Yes, with branding + backend discipline** |
| Support explainability requirements? | **Partially** — needs custom why/evidence/contributor UI |
| Connect to Hermes/orchestration? | **Yes via integration façade** (preferred over direct model chat) |
| Future project/task/memory visibility? | **Plausible with extensions**; not turnkey |

## Security

When deployed later: Traefik-only ingress, auth enabled, no unnecessary tool bridges from the UI process. UI must not hold admin credentials for homelab Execute paths.

## Maintenance

Track upstream releases; pin versions; limit plugins. Prefer thin customizations over forks.

## Integration

**Required pattern:** Open WebUI → KORA Orchestration façade → (Council/Memory/Knowledge/Agents/Tools).

**Forbidden pattern:** Open WebUI → model/tools as the system of intelligence, with Hermes/KORA as optional.

## Performance

Chat UX fine at homelab scale. Latency dominated by orchestration/models.

## Migration

UI is intentionally replaceable. Persist conversations only if Memory Runtime governance allows; do not treat UI chat DB as Knowledge.

## Community

Large active community; frequent releases—pin and test upgrades.

## Operational Complexity

One more service in the eventual stack; keep config minimal.

## Governance

Approvals for Execute/Administrative actions remain KORA UX contracts—not “click run in the UI plugin.”

## Alternatives Considered

| Alternative | Pros | Cons |
| --- | --- | --- |
| Custom UI only | Perfect UX fit | Slowest path |
| Other chat UIs | Similar | Similar extension work |
| Hermes TUI/channels as primary UX | Already in substrate | Weak explainability/Council modes; identity risk |
| Open WebUI | Mature chat UX | Feature gravity toward second brain |

## Decision

**Provisionally Adopt** Open WebUI as the **UI layer candidate**.

**Decision statement:** Open WebUI may front KORA for chat interaction in future spikes/implementations only when routed through KORA orchestration and presented as KORA. Built-in agent/RAG features are non-authoritative and must not redefine Memory/Knowledge/Council.

**Constraints / conditions:**

1. Open WebUI is **not** KORA.
2. Product identity, synthesis, and governance live behind the orchestration façade.
3. No raw chain-of-thought exposure; follow `Explainability.md`.
4. Do not use Open WebUI as Knowledge authority or Memory Runtime.
5. No Docker/compose authorized by this ADR alone.

**Rollback plan:** Point users to an alternate client against the same façade; discard UI-only state.

## Consequences

**Positive:** Fast path to a usable chat surface; replaceable UI.

**Negative:** Feature creep risk; Council/memory/approval UX still custom work.

## Implementation Notes

Wire to ADR-0004 façade when a spike is authorized. Theme/name as KORA. Disable or ignore competing built-in “assistant platform” paths where they conflict.
