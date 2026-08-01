# KORA Runtime Profiles

**Status:** Canonical runtime-profile specification (Phase 13.14)  
**Platform:** KORA / Brainiac (`KORA.md`)  
**Rule:** Profiles change *how* KORA is implemented on hardware. They do **not** change *what* KORA is.

Companions: `Runtime_Contracts.md`, `Runtime_Observability.md`, `Runtime_State.md`, `Implementation_Architecture.md`

---

## Purpose

Define how the same KORA architecture can operate across different hardware and model capabilities while preserving all Phase 13 contracts.

Every profile must produce the **same observable behavior** for the user and the same architectural guarantees. Profiles differ only in internal realization.

---

## Invariant Across All Profiles

| Invariant | Requirement |
| --- | --- |
| Identity | User-facing product is **KORA / Brainiac** only |
| Council | Dynamics/Selection/Deliberation/Voting remain authoritative |
| Separations | Council ≠ Agents; Memory ≠ Knowledge; Knowledge ≠ Tools; Tools ≠ Decisions |
| Context path | Classification → strategy → retrieval → ranking → assembly → Council → response |
| Explainability | Structured why/evidence/contributors; no raw CoT |
| Provenance | Labels survive every hop |
| Governance | No silent Memory write; no silent Knowledge promotion; Execute gated |
| Graphify | Deferred / off default path |
| Obsidian | External workflow only |

If a profile cannot uphold these, it is invalid—not “a different KORA.”

---

## Profile Summary

| Profile | Hardware posture | Council realization | Current target? |
| --- | --- | --- | --- |
| **1 — Solo Runtime** | Single local LLM | Conceptual Council; KORA reasons directly under Dynamics | **Yes (near-term)** |
| **2 — Simulated Council** | Single model | Structured multi-member prompting; no independent member runtimes | Next step when Solo is stable |
| **3 — Distributed Council** | Multi-model / multi-service | Hermes (or equivalent) orchestrates independent member runtimes | Later |
| **4 — Hybrid Runtime** | Local + remote + specialized services | Any mix of Solo/Simulated/Distributed under same contracts | Later |

---

## Profile 1 — Solo Runtime

### Intent

Current target for constrained hardware and the disposable spike trajectory.

### Hardware

- Single local LLM (or single inference endpoint)
- Optional local Memory/Knowledge indexes (ADR-governed candidates)
- No requirement for per-member model instances

### Characteristics

| Concern | Behavior |
| --- | --- |
| Council | **No separate Council runtime.** KORA performs reasoning directly while **representing** Council Dynamics conceptually (selection metadata, contributor labels, disagreement surfacing) |
| Memory / Knowledge / Tools | Unchanged contracts |
| Explainability | Preserved; contributors may be synthesized under Dynamics rules, not invented as fake independent agents |
| Orchestration | Thin conductor path; Hermes optional/absent |

### Must

- Still classify, select strategy, retrieve selectively, rank, assemble, explain
- Still refuse Execute/Administrative without governance
- Still label Memory ≠ Knowledge

### Must not

- Pretend independent member models exist when they do not
- Collapse KORA into “just the local model brand”
- Skip Context Intelligence because only one model is available

---

## Profile 2 — Simulated Council

### Intent

Same single-model hardware as Solo, richer Council fidelity via structured prompting.

### Hardware

- Single model
- No independent member services

### Characteristics

| Concern | Behavior |
| --- | --- |
| Council | Members represented through **structured prompting** (roles, specialties, disagreement formats) |
| Independence | Logical separation only—not process isolation |
| UX | Identical user-facing identity and explainability shape to Solo/Distributed |

### Must

- Preserve Selection → Deliberation → Synthesis semantics
- Surface disagreement when Dynamics require it
- Keep Agents out of Council seats

### Must not

- Leak prompt scaffolding as raw CoT to the user
- Treat simulated members as Agents or Tools

---

## Profile 3 — Distributed Council

### Intent

Scale deliberation across independent member runtimes when hardware/services allow.

### Hardware

- Multiple models and/or services
- Orchestration substrate (Hermes candidate per ADR-0004) coordinates workers/members

### Characteristics

| Concern | Behavior |
| --- | --- |
| Council | Members may be independent model/service instances |
| Orchestration | Hermes (or equivalent) coordinates; **does not replace KORA identity** |
| User face | KORA remains sole user-facing identity |

### Must

- Map member runtimes to Council seats under Dynamics—not to disposable agents by default
- Aggregate contributions through KORA synthesis
- Preserve provenance across member hops

### Must not

- Expose Hermes/Open WebUI/member brands as the product
- Allow a member runtime to Execute outside Tools governance
- Bypass Context Intelligence / contracts because “models talk to each other”

---

## Profile 4 — Hybrid Runtime

### Intent

Combine local models, remote models, and specialized services without rewriting architecture.

### Hardware

- Mix of local inference, remote APIs, specialized Memory/Knowledge/Tool services

### Characteristics

| Concern | Behavior |
| --- | --- |
| Placement | Any concern may run local or remote **if contracts hold** |
| Council | May mix Solo/Simulated/Distributed techniques per capability |
| Data residency | Secrets and governed Memory stay under homelab policy |

### Must

- Document which concern runs where without changing ownership
- Keep repo/ADRs as Knowledge SoT; indexes remain non-authority
- Fail closed on missing remote services (uncertainty, not fabrication)

### Must not

- Let remote vendors redefine identity, Memory, or Knowledge authority
- Require Graphify or Obsidian for core path

---

## Profile Selection Guidance

| Choose | When |
| --- | --- |
| Solo | Single LLM; validate architecture end-to-end; current spike target |
| Simulated | Same hardware; need stronger Council fidelity before multi-model cost |
| Distributed | Capacity for independent member runtimes; orchestration façade ready |
| Hybrid | Heterogeneous infrastructure with clear contract compliance |

Promotion between profiles is an **implementation choice**, not an architecture rewrite. Contracts (`Runtime_Contracts.md`) stay fixed.

---

## Observability & State

All profiles must emit the same conceptual observability events (`Runtime_Observability.md`) and follow the same state lifecycle (`Runtime_State.md`).

---

## Non-goals

- Selecting final models or vendors
- Docker/compose/production deployment
- Changing Council/Memory/Knowledge/Tool architecture documents
- Mandating Distributed Council before Solo is validated

---

## Document Map

| Document | Role |
| --- | --- |
| `Runtime_Profiles.md` (this file) | Hardware/implementation profiles |
| `Runtime_Contracts.md` | Observable I/O contracts |
| `Runtime_Observability.md` | Trace/provenance requirements |
| `Runtime_State.md` | Lifecycle ownership |
| `Documentation/Phase13/Runtime_Profile_Model.md` | Phase 13.14 report |
