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
| [Council/Dynamics.md](Council/Dynamics.md) | Authoritative Council operating specification |
| [Council/](Council/) | Council structure, members, selection, voting |

Working roadmap: `Documentation/Phase13/Phase13_Roadmap.md`  
Alignment record: `Documentation/Phase13/KORA_Architecture_Alignment.md`  
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
         Memory / Knowledge / Tools
                     |
          Homelab Environment
```

KORA is **part of the Council**, not above it.

---

## Separation of responsibilities

| Concern | Responsibility | Document |
| --- | --- | --- |
| **KORA** | Platform identity, facilitation, synthesis, user-facing intelligence | `KORA.md` |
| **Council** | Specialized collective reasoning | `Council/` (Dynamics authoritative) |
| **Memory** | Persistent knowledge of past interactions and decisions | `Memory.md` |
| **Knowledge** | Reference information | Phase 13.2 (planned); repo as interim substrate |
| **Tools** | External capabilities (MCP and related) | `MCP.md` |
| **Agents** | Temporary execution entities | `Agents.md` |
| **Models** | Underlying inference engines | `Models.md` |
| **Future** | Sequencing and open questions | `FuturePlans.md` |

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
3. **Separation of Responsibilities** — Reasoning, memory, knowledge, tools, agents, and models stay distinct.
4. **User-First Outcomes** — The requester is the highest priority.
5. **Governance Conformance** — Phase 13 builds on the Phase 12 production baseline; no infrastructure changes are implied by these docs alone.

---

## Document index

| Path | Contents |
| --- | --- |
| `KORA.md` | Complete KORA architecture definition |
| `Council/README.md` | Council directory entry |
| `Council/Dynamics.md` | How the Council operates |
| `Council/Council.md` | Council overview stub |
| `Council/Selection.md` | Selection rules (to be formalized) |
| `Council/Voting.md` | Voting rules (to be formalized) |
| `Council/Members/` | Canonical member specs + originals |
| `Memory.md` | Memory subsystem |
| `Models.md` | Model inventory / constraints (no tech lock-in here) |
| `MCP.md` | Tool / MCP architecture |
| `Agents.md` | Temporary agents vs Council roles |
| `FuturePlans.md` | Forward plans and sequencing notes |
