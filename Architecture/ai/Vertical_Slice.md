# KORA Thin Vertical Slice Architecture

**Status:** Canonical prototype-architecture specification (Phase 13.9)  
**Platform:** KORA / Brainiac (`KORA.md`)  
**Companions:** `Prototype_Boundaries.md`, `Integration_Flow.md`, `Implementation_Architecture.md`  
**Rule:** Validate interfaces end-to-end. Do not deploy. Do not rewrite architecture around tools.

Phase 13.0–13.8 defined identity, subsystems, runtimes, UX, implementation layers, and evaluation ADRs.  
Phase 13.9 defines the **minimum end-to-end workflow** that proves those contracts can compose.

---

## Purpose

Prove that a single user request can travel through KORA’s architectural interfaces and return a governed recommendation with explainability—without collapsing Council ≠ Agents, Memory ≠ Knowledge, Knowledge ≠ Tools, or Tools ≠ Decisions.

This document is **architecture validation**. It does not authorize Docker, compose, installs, or production automation.

---

## Minimum Workflow

```text
User Request
    ↓
Interface
    ↓
Orchestration
    ↓
KORA Classification
    ↓
Council Selection
    ↓
Context Assembly
    ↓
Knowledge / Memory Retrieval
    ↓
Council Deliberation
    ↓
Recommendation
    ↓
Explainability Output
```

### Stage meanings

| Stage | Architectural owner | Purpose |
| --- | --- | --- |
| **User Request** | User | States objective, constraints, and desired outcome |
| **Interface** | UI Layer | Captures request; presents KORA identity; returns recommendation + explanation |
| **Orchestration** | Orchestration Layer | Routes the turn into KORA’s conductor path (substrate candidates governed by ADRs) |
| **KORA Classification** | KORA | Classifies request type, sensitivity, and required capabilities (`Council/Selection.md`) |
| **Council Selection** | KORA + Council ops | Selects active/deferred members; never promotes agents into seats |
| **Context Assembly** | KORA | Builds minimum sufficient, provenance-labeled context (`Context_Assembly.md`) |
| **Knowledge / Memory Retrieval** | Knowledge Runtime + Memory Runtime | Retrieves reference vs continuity artifacts separately |
| **Council Deliberation** | Council | Specialty contributions under Dynamics; not majority voting |
| **Recommendation** | KORA synthesis | User-facing advice; tools/agents do not decide |
| **Explainability Output** | KORA / UX | Structured why/evidence/contributors without raw CoT |

---

## Required Inputs

Conceptual inputs to a successful slice turn:

| Input | Required? | Notes |
| --- | --- | --- |
| User request text (or equivalent message) | Yes | Objective + constraints |
| Session / conversation context (Temporary Context) | Yes (minimal) | Immediate dialogue coherence only |
| Classification result | Yes | Produced by KORA before selection |
| Council selection record | Yes | Active/deferred members + rationale |
| Assembled context package | Yes | Provenance-labeled; minimum sufficient |
| Memory retrieval results (may be empty) | Yes as a call result | Empty is valid; never unlabeled as Knowledge |
| Knowledge retrieval results (may be empty) | Yes as a call result | Empty is valid; never unlabeled as Memory |
| Tool evidence | Optional | Slice may omit live tools; if present, evidence ≠ decision |
| Agent results | Optional | Slice may omit agents; if present, workers ≠ Council |

**Not required for the thin slice:** Graphify relationship graph, Execute/Administrative tools, durable Memory writes, MCP server installs.

---

## Required Outputs

| Output | Required? | Notes |
| --- | --- | --- |
| Recommendation | Yes | Clear advised path or answer |
| Explainability object | Yes | Per `Explainability.md` fields (summary rationale, evidence, provenance, confidence, …) |
| Provenance labels on evidence | Yes | Source class: Memory / Knowledge / Tool / Agent / Conversation |
| Council contributor list | Yes when Council engaged | Empty/Invisible mode still records process metadata internally |
| Classification + selection audit fields | Yes | Enough to answer “why these members?” |
| Refusal / failure payload | When failing | Structured; not silent success |

Outputs must **not** include raw chain-of-thought dumps.

---

## Boundaries

### Preserved separations

| Boundary | Slice rule |
| --- | --- |
| **Council ≠ Agents** | Deliberation uses Council members; agents (if any) only return scoped results |
| **Memory ≠ Knowledge** | Separate retrieval calls; separate labels in context and explanation |
| **Knowledge ≠ Tools** | Retrieval is reference; tools are live evidence |
| **Tools ≠ Decisions** | Evidence informs; KORA/Council synthesize recommendation |
| **UI ≠ KORA** | Interface presents KORA; does not become the intelligence |
| **Orchestration substrate ≠ KORA identity** | Hermes (if used later) is behind the conductor façade |
| **Indexes ≠ SoT** | Chroma/Graphify (if used later) never outrank repo/ADRs |

### Layer ownership in the slice

```text
UI .............. present / collect
Orchestration ... route / invoke conductor path
KORA ............ classify, assemble, synthesize, explain
Council ......... deliberate under Dynamics
Memory Runtime .. continuity retrieval (read path in slice)
Knowledge Runtime reference retrieval (read path in slice)
Tools/Agents .... optional; out of default thin-slice path
```

---

## Provenance Requirements

Every evidence item entering Context Assembly or Explainability must carry:

| Field | Meaning |
| --- | --- |
| **source_class** | `memory` \| `knowledge` \| `tool` \| `agent` \| `conversation` \| `user` |
| **source_ref** | Document path, memory id, tool call id, or equivalent |
| **authority_or_confidence** | Authority tier (Knowledge) or confidence (Memory) when applicable |
| **freshness** | As-of timestamp or “unknown” |
| **retrieval_reason** | Why this item was selected for this request |

Rules:

1. Memory must never be labeled as Knowledge authority.
2. Tool/agent outputs must never be labeled as Authoritative Knowledge by default.
3. Missing provenance → do not treat as authoritative; prefer omission or explicit “unverified.”
4. Explainability surfaces provenance without exposing private CoT.

---

## Failure Handling

| Failure | Expected behavior |
| --- | --- |
| Interface cannot reach orchestration | User-visible error; no partial “success” recommendation |
| Classification uncertain | Prefer safer/narrower Council selection; state assumptions |
| Memory/Knowledge retrieval unavailable | Continue with conversation + explicit “retrieval unavailable” note; reduce confidence |
| Empty retrieval | Valid; do not invent sources |
| Council deliberation incomplete | Recommend only with stated gaps, or refuse if unsafe |
| Provenance missing on critical claim | Do not assert as authoritative; escalate uncertainty |
| Request requires Execute/Administrative action | **Refuse action** in this slice; may recommend a human-governed next step |
| Safety / secrets risk | Refuse; never store or echo secrets |

Failures must preserve governance: no silent autonomous remediation of infrastructure.

---

## Technology Neutrality

The workflow is defined in architectural terms. ADR-governed candidates (Open WebUI, Hermes, Honcho, ChromaDB, Graphify) may later implement layers, but:

- Interfaces are not rewritten to match vendor APIs
- Slice success is measured by contract compliance, not product demos
- No install is authorized by this document

Mapping of candidates → layers: `Integration_Flow.md` and ADR-0004–0008.

---

## Success Criteria (Architecture Validation)

The thin vertical slice architecture is valid when:

1. End-to-end flow is fully specified (this document)
2. Prototype scope is controlled (`Prototype_Boundaries.md`)
3. Component interactions and non-flows are explicit (`Integration_Flow.md`)
4. Separations above are enforceable in a future spike without rewriting Phase 13.0–13.8 docs

---

## Document Map

| Document | Role |
| --- | --- |
| `Vertical_Slice.md` (this file) | Minimum E2E workflow + I/O + provenance + failure |
| `Prototype_Boundaries.md` | Allowed / forbidden prototype proofs |
| `Integration_Flow.md` | Conceptual data movement and ownership |
| `Documentation/Phase13/Vertical_Slice_Model.md` | Phase 13.9 report |
