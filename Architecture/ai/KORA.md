# KORA — Knowledge-Oriented Response Assistant

**Status:** Canonical architecture definition (Phase 13.0)  
**Also known as:** Brainiac  

KORA is Brainiac. KORA is not a separate engine beneath Brainiac. KORA is the primary AI entity of the homelab AI platform and the coordinating intelligence of the Council.

This document defines the **system architecture** of KORA.  
Council behavior is authoritative in `Council/Dynamics.md`.  
Council member character and operational voice live under `Council/Members/`.

---

## Identity

| Field | Value |
| --- | --- |
| Name | KORA |
| Acronym | K.O.R.A. |
| Full name | Knowledge-Oriented Response Assistant |
| Platform name | Brainiac (synonym for KORA — not a parent system) |
| Council role | Member; Chair; Conductor; First Among Equals |
| Primary titles | The Conductor |

KORA is:

- Brainiac
- A member of the Council
- Council Chair and Conductor
- First Among Equals
- The user-facing intelligence of the platform
- The orchestrator and synthesizer of Council deliberation

KORA is not:

- A separate runtime “beneath” Brainiac
- A replacement for the Council
- A manager of Council members as employees or sub-agents
- A monopoly on correctness

---

## Purpose

KORA exists to transform user requests into coherent, actionable guidance by coordinating specialized Council reasoning with memory, knowledge, tools, and models—while remaining accountable to the user.

Primary outcomes:

1. Understand the request and its context.
2. Select the minimum relevant Council expertise.
3. Facilitate challenge, synthesis, and clarity.
4. Present a recommendation the user can act on.
5. Preserve continuity through memory and governed knowledge over time.

---

## Role within the Council

The Council is a **collective reasoning framework**. KORA participates in reasoning while also facilitating the process.

```text
                KORA / Brainiac
                     |
             Council Reasoning
 +---------+---------+---------+---------+
 |         |         |         |         |
NOVA     IRIS     TALIA     SOLA      LUMA
 |         |         |
ALUMA    NOMA
                     |
         ---------------------------------
         |              |                |
     Knowledge       Memory           Agents
     "What exists?" "What happened?"  "Do work"
                                         |
                                      Tools
                                         |
                                   Environment
```

**Architectural rule:** KORA is part of the Council, not above it.

| Role aspect | Meaning |
| --- | --- |
| Member | Contributes the coordination specialty: relevance, pacing, synthesis, fairness |
| Chair / Conductor | Classifies requests, selects participants, sequences challenge, closes deliberation |
| First Among Equals | Holds process responsibility without hierarchical supremacy of judgment |
| User-facing voice | Delivers the Council’s recommendation to the requester |

Authoritative operating rules: `Council/Dynamics.md`.

---

## Responsibilities

### In scope

- Request classification and problem framing
- Contextual member selection (selective participation)
- Facilitation of respectful disagreement
- Synthesis of complementary perspectives
- Transparent presentation of residual disagreement
- Assembly of user-facing recommendations
- Coordination of access to memory, knowledge, and tools **as capabilities of KORA**, not as peer Council members
- Preservation of user-first priority

### Out of scope

- Replacing specialized Council reasoning with a single generalist answer by default
- Treating Council members as disposable sub-agents or task workers
- Owning persistent memory storage semantics (see `Memory.md` / `Memory_Runtime.md`)
- Owning knowledge corpus implementation (see `Knowledge.md` / `Knowledge_Runtime.md`)
- Owning context compiler implementation (see `Context_Assembly.md`)
- Owning raw model serving topology (see Models)
- Owning MCP server implementation details (see MCP)
- Owning ephemeral execution agents as permanent identity (see Agents)

---

## Cognitive Model

KORA’s cognition is **orchestrated multi-perspective reasoning**, not monolithic completion.

| Layer | Responsibility |
| --- | --- |
| **Council** | Reasoning — specialized perspectives under facilitation |
| **Memory** | What KORA remembers — interactions, decisions, preferences, lessons |
| **Knowledge** | What information exists — reference docs, standards, inventories, curated corpora |
| **Tools** | Live environment capability — what is true now / what can be interacted with |
| **Agents** | Temporary execution — do work (not Council seats) |
| **Models** | Underlying inference engines |

### Architecture principles

1. **KORA First** — All AI capabilities exist as part of KORA’s platform identity (Brainiac).
2. **Council as Cognitive Framework** — Members provide specialized reasoning perspectives.
3. **Separation of Responsibilities** — Reasoning, memory, knowledge, tools, agents, and models remain distinct concerns. **Memory ≠ Knowledge. Council ≠ Agents. Tools ≠ Decisions.**
4. **Selective Participation** — Not every request requires every member.
5. **Synthesis over Competition** — Collaboration refines the recommendation; dominance is a failure mode.
6. **User-First Outcomes** — Internal brilliance that does not help the user is incomplete.
7. **Delegated Execution under Governance** — Agents are created for bounded work, evaluated by KORA, and terminated; they never outrank Council judgment.
8. **Tool Evidence under Permission** — External interaction uses governed tools; evidence informs decisions but does not replace them.

---

## Relationship with Council Members

Council membership (canonical):

| Member | Archetype |
| --- | --- |
| KORA | The Conductor / Chair |
| NOVA | The Strategist |
| IRIS | The Seer |
| TALIA | The Philosopher |
| SOLA | The Heart |
| LUMA | The Historian |
| ALUMA | The Engineer |
| NOMA | The Tactician |

Relationship rules:

- Members are **peers in judgment** within their specialties.
- KORA coordinates process; members own specialty substance.
- KORA may invite, sequence, reframe, and synthesize — not veto expertise without transparent rationale to the user.
- Pairings and tensions (for example NOVA/NOMA, NOVA/ALUMA, TALIA/SOLA, IRIS/LUMA) are features of the cognitive framework, documented in member specs and Dynamics.

Detail and voice: `Council/Members/*.md`.  
Behavior of the collective: `Council/Dynamics.md`.

---

## Request Lifecycle

Generalized lifecycle for a user request:

1. **Receive** — User request enters KORA (Brainiac).
2. **Classify** — KORA determines problem type, stakes, constraints, and required specialties.
3. **Assemble context** — Relevant memory, knowledge, and tool results are gathered (as needed).
4. **Select Council** — Invite only members whose expertise materially affects the outcome.
5. **Deliberate** — Selected members contribute; cross-challenge and refinement occur.
6. **Synthesize** — KORA weaves convergent points, trade-offs, and residual disagreement.
7. **Respond** — User receives the recommendation (and transparent minority concerns when material).
8. **Persist (when appropriate)** — Decisions, preferences, and lessons may enter memory/knowledge under governance rules (Phase 13.2+).

If the problem class changes mid-session, KORA may expand or reduce membership and resume deliberation.

---

## Context Assembly

Context assembly is KORA’s responsibility as the user-facing coordinator. It is **not** a Council member.

Canonical specification: `Context_Assembly.md`.

```text
User Request
Conversation Context
Relevant Memory
Relevant Knowledge
Live Tool Evidence
Council Selection
Agent Results
        =
   KORA Context
```

Typical context classes:

| Class | Examples | Concern owner (architecture) |
| --- | --- | --- |
| Conversational | Current thread, recent turns | Memory / Temporary Context |
| Decision history | Prior recommendations and outcomes | Memory |
| Reference | Standards, runbooks, inventories, ADRs | Knowledge |
| Live environment | Host/service state via tools | Tools |
| Agent outputs | Scoped execution results | Agents → evaluated by KORA |
| Council state | Active members, open disagreements | Council / Dynamics |

Assembly principles:

- Prefer minimum sufficient context.
- Do not flood deliberation with irrelevant archives.
- Separate **what was remembered** (memory) from **what exists by reference** (knowledge) from **what is true now** (tools).
- Keep provenance labels on assembled fragments (`memory` | `knowledge` | `tool` | `agent` | …).
- Prefer Knowledge for standards and baseline claims; Prefer Tools for live state; Prefer Memory for user continuity.
- Memory/tool/generated content must not silently become Authoritative Knowledge.

Detailed runtime: `Memory_Runtime.md`, `Knowledge_Runtime.md`, `Context_Assembly.md`.

---

## Memory Relationship

Memory is a **subsystem of KORA**, not a Council peer.

Memory holds persistent traces of interactions and decisions so KORA and the Council can remain continuous across sessions.

| Memory does | Memory does not |
| --- | --- |
| Persist prior decisions and preferences | Replace Council reasoning |
| Support continuity and learning | Act as live environmental truth without tools |
| Inform LUMA/IRIS-style historical and pattern work with durable records | Select models or own MCP servers |

See `Memory.md` for boundaries and `Memory_Runtime.md` for lifecycle/governance.

---

## Knowledge Relationship

Knowledge is a **subsystem of KORA**: reference information that answers *what information exists?*

| Knowledge does | Knowledge does not |
| --- | --- |
| Provide authoritative reference material | Substitute for Council deliberation |
| Ground recommendations in governed sources | Equal “whatever was said in chat” (that is Memory) |
| Support retrieval, attribution, and freshness awareness | Own Council facilitation |
| Inform members with shared source material | Make the final decision |

**Knowledge informs reasoning. Knowledge does not make decisions.**

Canonical specification: `Knowledge.md`  
Runtime acquisition/validation/promotion: `Knowledge_Runtime.md`  
The repository remains the primary interim knowledge substrate until runtime ingestion/retrieval is authorized.

---

## Tool Relationship

Tools are a **subsystem of KORA**: external capabilities that answer *what is true right now?* and *what can be interacted with?*

```text
KORA
  |
Council Reasoning
  |
Agent Delegation
  |
Tool Layer
  |
External Environment
```

| Tools do | Tools do not |
| --- | --- |
| Provide live evidence and bounded actions | Make decisions or replace Council judgment |
| Expose capabilities (often via MCP-style protocols) | Equal Knowledge or Memory |
| Enforce permission ceilings (Read→Administrative) | Bypass Phase 12 baseline / change control |
| Return provenance-labeled results | Silently mutate authoritative Knowledge |

**Tools are not intelligence.** Tool output is evidence for KORA/Council evaluation.

Canonical specification: `Tools.md`  
Protocol architecture: `MCP.md`

---

## Agents Relationship

Agents are a **subsystem of KORA**: temporary execution capability that answers *do work*.

```text
                    KORA
                      |
              Council Reasoning
                      |
     ---------------------------------
     |              |                |
 Knowledge       Memory           Agents
 "What exists?" "What happened?"  "Do work"
                                     |
                                  Tools
```

| Agents do | Agents do not |
| --- | --- |
| Execute bounded tasks under KORA | Replace or become Council members |
| Gather, analyze, draft, run scoped work | Override Council synthesis |
| Use Tools within conceptual permission levels | Own permanent Memory or silently mutate authoritative Knowledge |
| Return results for KORA evaluation then terminate | Persist as personalities or parallel Brainiac identities |

**Council Member ≠ Agent.**  
Council members provide judgment. Agents complete tasks.

Canonical specification: `Agents.md`.

---

## Models Relationship

Models are **underlying inference engines**. They power KORA and may power specialized Council perspectives or agents, but they are not the architecture’s identity layer.

| Models do | Models do not |
| --- | --- |
| Provide inference capacity | Define who KORA is |
| Impose hardware and quality constraints | Replace Dynamics or member specs |
| Support embeddings/retrieval where designed | Dictate Council philosophy |

See `Models.md`. Runtime selection is deferred; this phase does not choose technologies.

---

## User Experience Relationship

KORA is the primary user-facing intelligence. Interfaces are windows into KORA—not separate products.

UX must expose enough structure for trust:

- Council visibility modes (Invisible / Advisory / Full)
- Memory inspect/correct/delete
- Knowledge provenance exploration
- Tool evidence labeling
- Agent task boundaries
- Explainability without raw chain-of-thought

Canonical specs: `User_Experience.md`, `Interaction_Model.md`, `Explainability.md`.

---

## Relationship to Homelab Environment

KORA operates **on top of** the governed Phase 12 production baseline. The homelab is the environment of truth for infrastructure questions; KORA must not invent a parallel undocumented platform.

Constraints:

- Respect `Documentation/Phase12.5/Production_Baseline.md`.
- Do not regress Phase 12 networking or appdata conventions without explicit change control.
- Prefer repository and tool-backed facts over unsupported assertion.

---

## Document Map

| Document | Role relative to KORA |
| --- | --- |
| `KORA.md` (this file) | Canonical platform / cognitive architecture |
| `README.md` | Entry point and document index |
| `Council/Dynamics.md` | Authoritative Council behavior |
| `Council/Members/` | Member identity, voice, relationships |
| `Memory.md` | Memory subsystem boundaries |
| `Memory_Runtime.md` | Memory lifecycle and governance runtime |
| `Knowledge.md` | Knowledge subsystem (what information exists) |
| `Knowledge_Runtime.md` | Knowledge acquisition/validation/promotion runtime |
| `Context_Assembly.md` | How KORA builds reasoning context |
| `User_Experience.md` | UX philosophy and interaction contract |
| `Interaction_Model.md` | User-facing interaction patterns |
| `Explainability.md` | Why/evidence/contributors without raw CoT |
| `Implementation_Architecture.md` | Implementation layers & tech evaluation framework |
| `Technology_Evaluation_ADR_Template.md` | ADR criteria for technology candidates |
| `Vertical_Slice.md` | Thin vertical slice E2E workflow (Phase 13.9) |
| `Prototype_Boundaries.md` | Prototype allowed / forbidden scope |
| `Integration_Flow.md` | Conceptual layer integration & provenance flow |
| `Architecture/decisions/ADR-0004`–`ADR-0008` | Phase 13.8 technology evaluation ADRs |
| `Documentation/Phase13/Technology_Evaluation_ADR_Model.md` | Phase 13.8 evaluation report |
| `Documentation/Phase13/Vertical_Slice_Model.md` | Phase 13.9 vertical slice report |
| `Tools.md` | Tool layer architecture |
| `MCP.md` | Conceptual MCP / protocol integration architecture |
| `Agents.md` | Temporary execution entities |
| `Models.md` | Inference engines |
| `FuturePlans.md` | Forward sequencing notes |

---

## Future Evolution

Implementation planning framework: `Implementation_Architecture.md`.

Expected tracks (implementation only when authorized by ADR; architecture first):

- Technology evaluation ADRs for UI / Orchestration / Memory / Knowledge / Tools (Phase 13.8: ADR-0004–0008)
- Thin vertical slice architecture (Phase 13.9: `Vertical_Slice.md`, `Prototype_Boundaries.md`, `Integration_Flow.md`)
- Thin vertical slices that preserve Council, Memory, Knowledge, Tools, Agents boundaries
- Client surfaces satisfying UX / Interaction / Explainability contracts
- Expansion of Council membership or capabilities without violating First Among Equals or Dynamics principles

Evolution must preserve:

- KORA ≡ Brainiac
- KORA as Council member and Conductor
- Separation of Council / Memory / Knowledge / Tools / Agents / Models
- User-first outcomes and governance conformance
- Technology serving architecture—not the reverse
- User-first outcomes and governance conformance
