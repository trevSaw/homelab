# AI Architecture

This directory defines the homelab **AI platform architecture**.

The platform identity is **KORA (Knowledge-Oriented Response Assistant)**.  
**KORA is Brainiac.** Brainiac is not a parent system above KORA.

KORA is the primary AI entity: user-facing intelligence, Council Chair/Conductor, and coordinator of memory, knowledge, tools, agents, and models. The Council is KORA’s collective reasoning framework—not a set of employees, and not a layer that replaces KORA.

---

## Start here

| Document | Purpose |
| --- | --- |
| [KORA.md](KORA.md) | Canonical KORA / Brainiac architecture |
| [Implementation_Architecture.md](Implementation_Architecture.md) | Implementation layers & technology evaluation framework |
| [Vertical_Slice.md](Vertical_Slice.md) | Thin vertical slice E2E workflow |
| [Prototype_Boundaries.md](Prototype_Boundaries.md) | Prototype allowed / forbidden scope |
| [Integration_Flow.md](Integration_Flow.md) | Conceptual integration & provenance flow |
| [Spike_Architecture.md](Spike_Architecture.md) | Prototype spike planning architecture |
| [Spike_Acceptance_Criteria.md](Spike_Acceptance_Criteria.md) | Spike measurable acceptance criteria |
| [Spike_Test_Plan.md](Spike_Test_Plan.md) | Spike test scenarios |
| [Runtime_Spike_Execution.md](Runtime_Spike_Execution.md) | Runtime spike execution & isolation (Phase 13.11) |
| [Technology_Evaluation_ADR_Template.md](Technology_Evaluation_ADR_Template.md) | Reusable tech-evaluation ADR template |
| [User_Experience.md](User_Experience.md) | UX philosophy and interaction contract |
| [Interaction_Model.md](Interaction_Model.md) | User-facing interaction patterns |
| [Explainability.md](Explainability.md) | Why/evidence/contributors without raw CoT |
| [Context_Assembly.md](Context_Assembly.md) | How KORA builds reasoning context |
| [Context_Intelligence.md](Context_Intelligence.md) | Classification-aware retrieval intelligence |
| [Retrieval_Strategies.md](Retrieval_Strategies.md) | Per-class retrieval policies |
| [Context_Ranking.md](Context_Ranking.md) | Ranking, budgets, pruning |
| [Context_Intelligence_Validation.md](Context_Intelligence_Validation.md) | Phase 13.13 runtime validation |
| [Runtime_Profiles.md](Runtime_Profiles.md) | Solo / Simulated / Distributed / Hybrid profiles |
| [Runtime_Contracts.md](Runtime_Contracts.md) | Observable runtime contracts |
| [Runtime_Observability.md](Runtime_Observability.md) | Trace / provenance observability requirements |
| [Runtime_State.md](Runtime_State.md) | Request lifecycle and state ownership |
| [Memory_Runtime.md](Memory_Runtime.md) | Memory lifecycle and governance runtime |
| [Knowledge_Runtime.md](Knowledge_Runtime.md) | Knowledge acquisition/validation/promotion runtime |
| [Memory.md](Memory.md) | What KORA remembers (continuity boundaries) |
| [Knowledge.md](Knowledge.md) | What information exists (reference knowledge) |
| [Tools.md](Tools.md) | Live environment tools (evidence, not decisions) |
| [MCP.md](MCP.md) | Conceptual MCP / tool protocol architecture |
| [Agents.md](Agents.md) | Temporary execution workers (Council ≠ Agents) |
| [Council/Dynamics.md](Council/Dynamics.md) | Authoritative Council operating specification |
| [Council/Selection.md](Council/Selection.md) | How KORA classifies requests and selects participants |
| [Council/Deliberation.md](Council/Deliberation.md) | Session lifecycle and contribution model |
| [Council/Voting.md](Council/Voting.md) | Deliberative synthesis (not majority voting) |
| [Council/](Council/) | Council structure, members, schemas, prompts |

Working roadmap: `Documentation/Phase13/Phase13_Roadmap.md`  
Alignment record: `Documentation/Phase13/KORA_Architecture_Alignment.md`  
Council ops report: `Documentation/Phase13/Council_Operational_Model.md`  
Knowledge report: `Documentation/Phase13/Knowledge_Architecture_Model.md`  
Agent report: `Documentation/Phase13/Agent_Architecture_Model.md`  
Tool report: `Documentation/Phase13/Tool_Architecture_Model.md`  
Runtime report: `Documentation/Phase13/Memory_Runtime_Model.md`  
UX report: `Documentation/Phase13/User_Experience_Model.md`  
Implementation framework: `Documentation/Phase13/Implementation_Architecture_Model.md`  
Technology evaluation ADRs: `Architecture/decisions/ADR-0004`–`ADR-0008` (see `ADRIndex.md`)  
Evaluation report: `Documentation/Phase13/Technology_Evaluation_ADR_Model.md`  
Vertical slice report: `Documentation/Phase13/Vertical_Slice_Model.md`  
Prototype spike report: `Documentation/Phase13/Prototype_Spike_Model.md`  
Runtime spike report: `Documentation/Phase13/Runtime_Spike_Report.md`  
Context intelligence report: `Documentation/Phase13/Context_Intelligence_Model.md`  
Context intelligence runtime report: `Documentation/Phase13/Context_Intelligence_Runtime_Report.md`
Runtime spike validation: `Validation/Phase13.11/`  
Context intelligence validation: `Validation/Phase13.13/`
Runtime profiles report: `Documentation/Phase13/Runtime_Profile_Model.md`
Production prerequisite: `Documentation/Phase12.5/Production_Baseline.md`

---

## Conceptual model

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

KORA is **part of the Council**, not above it.  
**Council Member ≠ Agent.** Agents are temporary workers, not reasoning seats.

---

## Separation of responsibilities

| Concern | Responsibility | Document |
| --- | --- | --- |
| **KORA** | Platform identity, facilitation, synthesis, user-facing intelligence | `KORA.md` |
| **Council** | Specialized collective reasoning | `Council/` (Dynamics authoritative) |
| **Memory** | What KORA remembers (conversations, decisions, preferences, lessons) | `Memory.md` / `Memory_Runtime.md` |
| **Knowledge** | What information exists (docs, standards, ADRs, references) | `Knowledge.md` / `Knowledge_Runtime.md` |
| **Context Intelligence** | Classification-aware select/filter/rank before assembly | `Context_Intelligence.md` |
| **Context Assembly** | Builds provenance-labeled reasoning context | `Context_Assembly.md` |
| **User Experience** | How humans interact with KORA; trust/transparency contract | `User_Experience.md` |
| **Interaction Model** | User-facing request patterns | `Interaction_Model.md` |
| **Explainability** | Why/evidence/contributors without raw CoT | `Explainability.md` |
| **Implementation Framework** | Layers, sequencing, tech evaluation rules | `Implementation_Architecture.md` |
| **Tools** | Live environment — what is true now / what can be interacted with | `Tools.md` / `MCP.md` |
| **Agents** | Temporary execution — do work (not Council seats) | `Agents.md` |
| **Models** | Underlying inference engines | `Models.md` |
| **Future** | Sequencing and open questions | `FuturePlans.md` |

**Memory ≠ Knowledge. Council ≠ Agents. Tools ≠ Decisions.** Context Assembly combines inputs with provenance; nothing in the substrate independently decides.

---

## Council members

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

Member specifications: `Council/Members/`.  
Do not duplicate member lore into subsystem docs.

---

## Architecture principles

1. **KORA First** — AI capabilities belong to the KORA platform.
2. **Council as Cognitive Framework** — Specialized perspectives, selective participation, synthesis over competition.
3. **Separation of Responsibilities** — Reasoning, memory, knowledge, tools, agents, and models stay distinct. Memory ≠ Knowledge. Council ≠ Agents. Tools ≠ Decisions.
4. **User-First Outcomes** — The requester is the highest priority.
5. **Governance Conformance** — Phase 13 builds on the Phase 12 production baseline; no infrastructure changes are implied by these docs alone.
6. **Delegated Execution under Governance** — Agents are scoped, evaluated, and terminated by KORA.
7. **Tool Evidence under Permission** — External interaction uses governed tools; evidence informs decisions but does not replace them.

---

## Document index

| Path | Contents |
| --- | --- |
| `KORA.md` | Complete KORA architecture definition |
| `Knowledge.md` | Knowledge architecture (reference information) |
| `Knowledge_Runtime.md` | Knowledge runtime (acquisition/validation/promotion) |
| `Memory.md` | Memory architecture (what KORA remembers) |
| `Memory_Runtime.md` | Memory runtime (lifecycle/governance) |
| `Context_Assembly.md` | Context assembly architecture |
| `User_Experience.md` | UX architecture |
| `Interaction_Model.md` | Interaction patterns |
| `Explainability.md` | Explainability contract |
| `Implementation_Architecture.md` | Implementation architecture framework |
| `Technology_Evaluation_ADR_Template.md` | Tech evaluation ADR template |
| `Council/README.md` | Council directory entry |
| `Council/Dynamics.md` | How the Council operates |
| `Council/Selection.md` | Request classification and member selection |
| `Council/Deliberation.md` | Session lifecycle and contribution model |
| `Council/Voting.md` | Deliberative synthesis (not majority voting) |
| `Council/Schemas/` | Conceptual session schemas |
| `Council/Prompts/` | Prompt architecture (conceptual) |
| `Council/Members/` | Canonical member specs, originals, template |
| `Council/Council.md` | Council overview stub |
| `Tools.md` | Tool architecture (live environment interaction) |
| `MCP.md` | Conceptual MCP / protocol integration architecture |
| `Agents.md` | Agent orchestration (temporary workers; not Council members) |
| `Models.md` | Model inventory / constraints (no tech lock-in here) |
| `FuturePlans.md` | Forward plans and sequencing notes |
