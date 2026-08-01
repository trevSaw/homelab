# Memory

Memory architecture for KORA: what KORA **remembers**.

**Status:** Boundary and role specification aligned with Phase 13.2 Knowledge Architecture.  
**Detailed memory runtime design:** Phase 13.5 (deferred).  
**Companion:** `Knowledge.md` — **Memory is not Knowledge. Do not merge them.**

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
| Traces of decisions, preferences, and outcomes | Live environment truth (`MCP.md` / tools) |
| Learned context from interaction history | Council reasoning (`Council/Dynamics.md`) |
| Inputs that help continuity-aware deliberation | Model serving topology (`Models.md`) |

Canonical platform definition: `KORA.md`.  
Canonical knowledge definition: `Knowledge.md`.

---

## Relationship to Knowledge

- Chat recollection is **Memory**, not authoritative Knowledge.
- Promotion of a remembered preference into durable Personal/Project Knowledge requires governance (see `Knowledge.md`).
- LUMA/IRIS-style work may use **both**: Knowledge for recorded reference, Memory for interaction continuity—without conflating provenance.

---

## Context assembly

During Council sessions, KORA assembles context from Memory + Knowledge + Tools with provenance labels.  
See `KORA.md` (Context Assembly) and `Council/Deliberation.md`.

---

## Status

- Boundaries vs Knowledge: **defined (Phase 13.2)**
- Full memory lifecycle, governance depth, and runtime: **Phase 13.5**
- No database or vendor selection in this document
