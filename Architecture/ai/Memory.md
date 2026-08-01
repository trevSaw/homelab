# Memory

Memory architecture for KORA: what KORA **remembers**.

**Status:** Boundary definition + pointer to runtime architecture (Phase 13.5).  
**Runtime specification:** `Memory_Runtime.md`  
**Companion:** `Knowledge.md` / `Knowledge_Runtime.md` — **Memory is not Knowledge. Do not merge them.**

---

## Core distinction

| System | Answers | Examples |
| --- | --- | --- |
| **Memory** | What does KORA remember? | Prior conversations, decisions with the user, preferences, lessons learned, session continuity |
| **Knowledge** | What information exists? | Documentation, standards, ADRs, manuals, inventories, curated references |
| **Tools** | What is true in the environment now? | Live state via MCP and related integrations |

---

## Role in the KORA architecture

Memory is a **subsystem of KORA**, not a Council member and not a separate AI identity.

| Memory owns | Memory does not own |
| --- | --- |
| Continuity across sessions | Reference truth / documentation corpus (`Knowledge.md`) |
| Traces of decisions, preferences, and outcomes | Live environment truth (`Tools.md` / `MCP.md`) |
| Learned context from interaction history | Council reasoning (`Council/Dynamics.md`) |
| Inputs that help continuity-aware deliberation | Model serving topology (`Models.md`) |

Canonical platform definition: `KORA.md`.  
Canonical knowledge definition: `Knowledge.md`.  
Runtime lifecycle/governance: `Memory_Runtime.md`.  
Context usage: `Context_Assembly.md`.

---

## Relationship to Knowledge

- Chat recollection is **Memory**, not authoritative Knowledge.
- Promotion of a remembered preference into durable Personal/Project Knowledge requires governance (`Knowledge_Runtime.md` promotion pipeline).
- LUMA/IRIS-style work may use **both**: Knowledge for recorded reference, Memory for interaction continuity—without conflating provenance.

**Hard rule:** Memory cannot silently become Knowledge.

---

## Context assembly

During Council sessions, KORA assembles context from Memory + Knowledge + Tools (+ agent results) with provenance labels.  
See `Context_Assembly.md`.

---

## Controlling principle

**The user controls personal memory.**

---

## Status

- Boundaries vs Knowledge: **defined**
- Memory runtime lifecycle & governance: **defined in `Memory_Runtime.md` (Phase 13.5)**
- No database or vendor selection in these documents
