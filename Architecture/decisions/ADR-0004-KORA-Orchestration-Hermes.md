---
title: ADR-0004 KORA Orchestration — Hermes
document_type: ADR
service: kora
owner: Homelab
status: Provisional Adopt
version: 0.2.0
last_reviewed: 2026-08-01
related_documents:
  - Architecture/ai/KORA.md
  - Architecture/ai/Implementation_Architecture.md
  - Architecture/ai/Agents.md
  - Architecture/ai/Tools.md
  - Architecture/ai/MCP.md
  - Architecture/ai/Council/Dynamics.md
  - Architecture/ai/Technology_Evaluation_ADR_Template.md
---

# ADR-0004 — KORA Orchestration (Hermes)

## Meta

| Field | Value |
| --- | --- |
| ADR ID | ADR-0004 |
| Title | KORA Orchestration — Hermes |
| Date | 2026-08-01 |
| Author | Homelab |
| Candidate technology | Hermes Agent (Nous Research) |
| Proposed implementation layer | Orchestration |
| Related architecture docs | `KORA.md`, `Agents.md`, `Tools.md`, `MCP.md`, Council Dynamics/Selection/Deliberation/Voting, `Implementation_Architecture.md` |

## Status

**Provisional Adopt** — Hermes is the preferred orchestration *substrate candidate* for a constrained, non-production spike. Not a production install authorization. KORA identity and Council contracts remain authoritative.

## Context

KORA requires an orchestration layer to classify requests, select Council members, assemble context, synthesize responses, enforce governance, and manage temporary agents (`Implementation_Architecture.md`). Phase 13.0–13.7 defined those contracts without selecting a framework.

Hermes Agent (Nous Research) is an open-source, self-hostable agent runtime with multi-agent delegation, MCP tool integration, memory-provider hooks (including Honcho), and multi-channel gateways. It must be evaluated as an **implementation substrate for KORA orchestration**, not as a rename or replacement of KORA.

## Candidate Summary

Hermes provides agent lifecycle, tool calling, subagent spawn/parallelism, MCP connectivity, and persistent session/memory hooks. In KORA mapping it would occupy the **KORA Orchestration Layer** only if wrapped so that:

- User-facing product identity remains **KORA / Brainiac**
- Council deliberation/synthesis rules remain first-class
- Temporary agents remain workers, not Council seats

## Architecture Fit

| Criterion | Assessment |
| --- | --- |
| Architecture Fit | **Conditional pass** — capable substrate; identity/Council mapping is custom work |
| KORA Alignment | **Risk** — product markets itself as “the agent”; must not become the brand |
| Council Compatibility | **Conditional** — multi-agent exists; Council ≠ Agents must be enforced in our layer |
| Memory/Knowledge Boundary | **Neutral/risk** — built-in memory/skills can blur Memory ≠ Knowledge if left default |
| Security | **Conditional** — self-host + sandbox options; tool blast radius must be gated |
| Governance | **Gap** — approval/Execute workflows are KORA UX, not Hermes defaults |
| Maintenance Burden | **Medium–high** — fast-moving project; ops + upgrade discipline required |
| Integration Complexity | **Medium** — MCP helps; Open WebUI / custom UI must talk to *our* orchestration façade |
| Migration Risk | **Medium** — skills/memory/session formats are Hermes-shaped; keep contracts above |
| Performance | **Adequate for homelab** if concurrency limits applied |
| Community / Project Health | **Strong** — active Nous Research stewardship; MIT |
| Operational Complexity | **Medium–high** — gateway, models, tools, memory providers |
| Decision | **Provisionally Adopt** (spike-gated) |

Evaluate checklist:

- [x] `KORA.md` — **only if** Hermes is hidden behind KORA conductor identity
- [~] Council model — **requires** Selection/Deliberation/Voting implemented as KORA logic, not generic swarm
- [~] Knowledge model — must not treat skills/chat as Authoritative Knowledge
- [~] Memory model — prefer external Memory Runtime contracts over silent defaults
- [x] Agents / Tools — strong temporary-agent + MCP path
- [~] UX / Explainability — must expose provenance/Council modes via our contracts

**Architecture fit notes:** Hermes can support KORA-as-conductor *if* we treat it as a runtime and implement Council orchestration ourselves. Native multi-agent is hierarchical worker decomposition—useful for Agents.md lifecycle, **not** a drop-in Council.

**Deal-breakers found:** None absolute. Soft deal-breaker if Hermes identity replaces KORA branding or if Council members are implemented as unconstrained autonomous agents without Dynamics.

### Specific evaluation questions

| Question | Answer |
| --- | --- |
| Support KORA as conductor? | **Yes, with custom conductor prompts/policies** — Hermes must not be the user-facing name |
| Coordinate Council reasoning? | **Partially native** — need explicit Selection → Deliberation → Synthesis pipeline |
| Manage temporary agents? | **Yes** — subagent spawn/terminate aligns with Agents.md |
| Preserve Council ≠ Agents? | **Only by policy** — Council seats must not be modeled as fire-and-forget workers |
| Future MCP/tool integration? | **Yes** — first-class MCP support |
| Unwanted coupling? | **Yes risk** — memory providers, skills, gateway channels can pull architecture off-contract |

## Security

- Prefer self-hosted deployment; no telemetry reliance for core path
- Tool/MCP surfaces require least privilege and Phase 12 network norms when eventually deployed
- Subagent isolation is necessary but insufficient—Execute/Administrative paths need KORA approval UX
- Secrets must never land in Hermes memory/skills stores

**Security notes:** Acceptable for a non-production spike with locked toolsets; production requires explicit permission model mapped to `Tools.md`.

## Maintenance

Fast upstream cadence; pin versions; document our façade. Skills auto-creation must be disabled or heavily gated so “self-improving agent” does not rewrite governance.

## Integration

- MCP: strong fit for Tools layer later
- Honcho: optional memory provider (see ADR-0005)—must not auto-adopt Memory Runtime
- UI: Open WebUI (ADR-0008) must call KORA orchestration façade, not treat Hermes CLI as the product

## Performance

Homelab-scale OK with concurrency caps. Multi-agent fan-out can amplify model cost/latency—Council selection should stay minimal-sufficient.

## Migration

Keep durable contracts (Council schemas, Memory/Knowledge APIs) outside Hermes-native stores. Export session/skill data before any lock-in assumption.

## Community

Nous Research / MIT; active docs and releases. Abandonment risk moderate-low relative to one-off frameworks; still pin and abstract.

## Operational Complexity

Gateway + models + tools + optional memory provider. Day-2 needs logs, version pins, and clear rollback to “architecture-only / no runtime.”

## Governance

Hermes does not replace ADR/repo governance. Administrative actions remain human-approved. Auditability of tool calls must be captured in our layer.

## Alternatives Considered

| Alternative | Pros | Cons |
| --- | --- | --- |
| Custom orchestration only | Perfect contract fit | Higher build cost; slower path to MCP/agents |
| LangGraph-class frameworks | Graph control flow | Still not Council; similar identity risk |
| Defer all orchestration runtime | Zero coupling | Blocks thin vertical slices |
| Hermes | MCP + agents + self-host | Identity/memory defaults fight KORA unless constrained |

## Decision

**Provisionally Adopt** Hermes as the preferred **orchestration substrate candidate**, subject to constraints below. This does **not** authorize Docker/compose/production deployment.

**Decision statement:** Hermes may be used for a time-boxed, non-production spike to prove KORA conductor + temporary agents + MCP hooks—only behind a KORA façade that preserves Council contracts.

**Constraints / conditions:**

1. User-facing identity is **KORA / Brainiac**, never Hermes.
2. Council members are advisory reasoning roles under Dynamics; they are **not** generic Hermes workers.
3. Temporary agents follow `Agents.md` create/evaluate/terminate; no permanent “staff agents.”
4. Built-in memory/skills must not silently become Knowledge or bypass Memory governance.
5. No Phase 12 infrastructure changes; no production compose in this ADR.
6. Spike must demonstrate Selection → Deliberation → Synthesis against Council docs before any broader adoption.

**Rollback plan:** Remove spike runtime; retain architecture docs and ADRs; no data treated as SoT. Swap orchestration substrate later without renaming KORA.

## Consequences

**Positive:** Accelerates MCP/agent plumbing; aligns with Implementation_Architecture sequencing; community momentum.

**Negative:** High risk of product-identity capture; memory/skill defaults may violate Memory ≠ Knowledge; operational surface grows early.

## Implementation Notes

Authorized next step is **planning a constrained spike** (separate change), not install-by-default. Compose/Docker remain out of scope until an explicit implementation phase + governance review.
