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
| [Agents.md](Agents.md) | Temporary execution workers (Council ≠ Agents) |
| [Knowledge.md](Knowledge.md) | What information exists (reference knowledge) |
| [Memory.md](Memory.md) | What KORA remembers (continuity) |
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
| **Memory** | What KORA remembers (conversations, decisions, preferences, lessons) | `Memory.md` |
| **Knowledge** | What information exists (docs, standards, ADRs, references) | `Knowledge.md` |
| **Tools** | External capabilities (MCP and related) | `MCP.md` |
| **Agents** | Temporary execution — do work (not Council seats) | `Agents.md` |
| **Models** | Underlying inference engines | `Models.md` |
| **Future** | Sequencing and open questions | `FuturePlans.md` |

**Memory ≠ Knowledge. Council ≠ Agents.** Context assembly combines Knowledge + Memory + Tools; agents may help gather but do not judge.

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
3. **Separation of Responsibilities** — Reasoning, memory, knowledge, tools, agents, and models stay distinct. Memory ≠ Knowledge. Council ≠ Agents.
4. **User-First Outcomes** — The requester is the highest priority.
5. **Governance Conformance** — Phase 13 builds on the Phase 12 production baseline; no infrastructure changes are implied by these docs alone.
6. **Delegated Execution under Governance** — Agents are scoped, evaluated, and terminated by KORA.

---

## Document index

| Path | Contents |
| --- | --- |
| `KORA.md` | Complete KORA architecture definition |
| `Knowledge.md` | Knowledge architecture (reference information) |
| `Memory.md` | Memory architecture (what KORA remembers) |
| `Council/README.md` | Council directory entry |
| `Council/Dynamics.md` | How the Council operates |
| `Council/Selection.md` | Request classification and member selection |
| `Council/Deliberation.md` | Session lifecycle and contribution model |
| `Council/Voting.md` | Deliberative synthesis (not majority voting) |
| `Council/Schemas/` | Conceptual session schemas |
| `Council/Prompts/` | Prompt architecture (conceptual) |
| `Council/Members/` | Canonical member specs, originals, template |
| `Council/Council.md` | Council overview stub |
| `Agents.md` | Agent orchestration (temporary workers; not Council members) |
| `Models.md` | Model inventory / constraints (no tech lock-in here) |
| `MCP.md` | Tool / MCP architecture |
| `FuturePlans.md` | Forward plans and sequencing notes |
