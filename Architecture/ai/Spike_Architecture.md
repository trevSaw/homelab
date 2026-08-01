# KORA Prototype Spike Architecture

**Status:** Canonical spike-planning specification (Phase 13.10)  
**Platform:** KORA / Brainiac (`KORA.md`)  
**Companions:** `Spike_Acceptance_Criteria.md`, `Spike_Test_Plan.md`, `Vertical_Slice.md`, `Prototype_Boundaries.md`  
**Authorization level:** **Planning only**

This phase defines how a controlled non-production spike **would** validate KORA.  
It does **not** authorize production deployment, Docker compose creation, service migration, permanent memory writes, MCP execution, or infrastructure changes.

---

## Spike Goals

Prove architectural assumptions safely:

1. End-to-end path from user message to explainable recommendation works under KORA contracts
2. Council selection and contribution remain distinct from agents
3. Memory and Knowledge retrieval stay separated with provenance
4. Product identity remains **KORA / Brainiac** (UI and orchestration are substrates)
5. Technology remains replaceable behind façades
6. Failure and uncertainty paths behave honestly (no silent authority)

Non-goals: autonomy, production ops, Execute tooling, durable Memory writes, Graphify integration (ADR-0007 Defer).

---

## Conceptual Flow

```text
User
 ↓
Open WebUI
 ↓
Hermes
 ↓
KORA Identity Layer
 ↓
Council Reasoning
 ↓
Context Assembly
 ↓
Knowledge / Memory Retrieval
 ↓
Explainable Response
```

Aligned with `Vertical_Slice.md` and `Integration_Flow.md`. Order of Knowledge/Memory retrieval vs assembly may be “retrieve then assemble” or “assemble queries then retrieve”; ownership does not change.

---

## Component Boundaries

| Component | Role in spike | Boundary |
| --- | --- | --- |
| **Open WebUI** | UI capture/render | Not KORA; not SoT; not Council |
| **Hermes** | Orchestration substrate | Behind KORA façade; not product brand |
| **KORA Identity Layer** | Conductor: classify, select, assemble, synthesize, explain | Owns policy; not rewritten by vendor defaults |
| **Council Reasoning** | Specialty deliberation under Dynamics | Members ≠ agents |
| **Context Assembly** | Provenance-labeled package | Minimum sufficient; no laundering |
| **Memory Retrieval** | Continuity read path | Memory ≠ Knowledge; no silent durable writes |
| **Knowledge Retrieval** | Reference read path | Index ≠ SoT; authority from repo/ADRs |
| **Explainable Response** | Recommendation + explanation object | No raw CoT |

**Out of spike path:** Graphify, MCP Execute/Administrative tools, permanent Memory write pipeline, Knowledge promotion automation, Phase 12 service changes.

---

## Allowed Technologies (Planning Map)

ADR-governed candidates that **may appear in a future authorized runtime spike plan**—not installed by this document:

| Technology | ADR | Spike role |
| --- | --- | --- |
| Open WebUI | 0008 Provisional Adopt | UI only |
| Hermes | 0004 Provisional Adopt | Orchestration substrate |
| Honcho | 0005 Spike | Optional Memory read-path experiment |
| ChromaDB | 0006 Provisional Adopt | Optional Knowledge retrieval index over governed docs |
| Graphify | 0007 Defer | **Excluded** from this spike |

Stubs are acceptable: Memory/Knowledge channels may return empty or fixture data if provenance and separation are still demonstrated.

---

## Forbidden Behaviors

| Forbidden | Why |
| --- | --- |
| Production deployment | Out of authorization |
| Docker compose creation under this phase | Explicit restriction |
| Service migration / Phase 12 changes | Infrastructure freeze |
| Permanent Memory writes | Requires governance UX; Prototype_Boundaries |
| MCP execution / live admin tools | Tools ≠ Decisions; blast radius |
| Autonomous actions / system modification | Same |
| Silent Memory → Knowledge promotion | Boundary |
| Treating Chroma (or any index) as authority | Knowledge SoT remains repo/ADRs |
| Replacing KORA identity with Hermes/Open WebUI branding | KORA ≡ Brainiac |
| Collapsing Council into disposable agents | Council ≠ Agents |
| Raw chain-of-thought exposure | Explainability |
| Installing Graphify in this spike | ADR-0007 Defer |

---

## Data Flow

### Moves

- User message + session id → UI → Hermes → KORA
- Classification + Council selection record (internal)
- Memory query/result (labeled `memory`, may be empty)
- Knowledge query/result (labeled `knowledge`, may be empty)
- Assembled context → Council contributions → KORA synthesis
- Recommendation + explainability object → UI

### Does not move

- Secrets
- Raw CoT
- Entire corpora
- Unlabeled merged Memory+Knowledge blobs
- Execute commands
- Durable Memory mutations
- Graphify graph payloads

Provenance must survive every hop (`Integration_Flow.md`).

---

## Rollback Philosophy

Assume any future runtime spike is **disposable**:

1. **Architecture first** — docs and ADRs remain SoT; spike code/config is experimental
2. **No Phase 12 coupling** — spike must not alter production compose/networks/appdata conventions
3. **Ephemeral state** — spike Memory/Knowledge stores are non-authoritative and deletable
4. **Kill switch** — disable UI→orchestration path; users lose nothing authoritative
5. **Replaceability** — swap Open WebUI or Hermes without renaming KORA or rewriting Council docs
6. **Evidence retention** — keep spike notes/results in `Documentation/Phase13/`; discard runtime data freely

If the spike falsifies an assumption, **update planning docs / ADRs**—do not silently reshape KORA identity to fit the tool.

---

## Authorization Statement

| Activity | Authorized by Phase 13.10? |
| --- | --- |
| Define spike architecture, acceptance, tests | **Yes** |
| Plan a future non-production experiment | **Yes (planning)** |
| Create compose / install candidates / change infra | **No** |
| Production cutover | **No** |

A later phase must explicitly authorize any runtime execution of this spike.

---

## Document Map

| Document | Role |
| --- | --- |
| `Spike_Architecture.md` (this file) | Goals, boundaries, flow, rollback |
| `Spike_Acceptance_Criteria.md` | Measurable success criteria |
| `Spike_Test_Plan.md` | Scenarios and expected behaviors |
| `Documentation/Phase13/Prototype_Spike_Model.md` | Phase 13.10 report |
