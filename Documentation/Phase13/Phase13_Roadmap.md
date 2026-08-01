# Phase 13 — AI Architecture & Knowledge Platform

**Status:** 🚧 IN PROGRESS  

**Start Date:** 2026-08-01  

**Prerequisite:** Phase 12 Production Baseline (`Documentation/Phase12.5/Production_Baseline.md`)  

**Primary Goal:** Design and implement the Brainiac (KORA) AI platform on top of the standardized homelab infrastructure.

This phase focuses on **architecture before implementation**.

Phase 13 shifts the project from infrastructure standardization toward the construction of the AI platform that will operate on top of the homelab. The focus becomes architecture, orchestration, memory, knowledge management, and intelligent services while preserving the stable production baseline established during Phase 12.

**Master roadmap entry:** `Architecture/standards/StandardsRoadmap.md`  
**Do not regress:** Phase 12 media `proxy`/`hotio` fabric or Monarch appdata conventions without an explicit change.

---

## Phase overview

| Sub-phase | Title | Status |
| --- | --- | --- |
| 13.1 | Council Architecture | 🚧 In Progress |
| 13.2 | Knowledge Architecture | 📋 Planned |
| 13.3 | Agent Orchestration | 📋 Planned |
| 13.4 | External Integrations | 📋 Planned |
| 13.5 | Knowledge & Memory Runtime | 📋 Planned |
| 13.6 | User Experience | 📋 Planned |

---

## Phase 13.1 — Council Architecture

**Objective:** Define the Council as the reasoning framework used by KORA.

**Status:** 🚧 In Progress

### Deliverables

- Council directory structure
- Council architecture
- Dynamics.md
- Member specifications
- Selection rules
- Voting rules
- Prompt architecture
- Canonical member template

### Working tree

Primary artifacts live under `Architecture/ai/Council/`, including member specifications, dynamics, and supporting configuration.

Council work begun 2026-08-01 is the starting workstream of Phase 13.

---

## Phase 13.2 — Knowledge Architecture

**Objective:** Design how KORA stores, retrieves, indexes, and reasons over information.

**Status:** 📋 Planned

### Planned deliverables

- Memory architecture
- Knowledge collections
- Long-term memory index
- Retrieval strategy
- Context assembly
- Knowledge lifecycle
- Memory governance

---

## Phase 13.3 — Agent Orchestration

**Objective:** Define how KORA coordinates reasoning and specialized capabilities.

**Status:** 📋 Planned

### Planned deliverables

- Hermes integration
- Council orchestration
- Prompt assembly
- Agent lifecycle
- Routing
- Context injection
- Conversation management

---

## Phase 13.4 — External Integrations

**Objective:** Connect KORA to the homelab ecosystem.

**Status:** 📋 Planned

### Planned deliverables

- Filesystem MCP
- Git MCP
- Docker MCP
- Home Assistant MCP
- Technitium DNS MCP
- Future MCP integrations

Integrations MUST respect the Phase 12 production baseline and existing governance standards (networking, secrets, compose SoT, documentation).

---

## Phase 13.5 — Knowledge & Memory Runtime

**Objective:** Implement the production memory system.

**Status:** 📋 Planned

### Planned deliverables

- Long-term memory
- Semantic retrieval
- Reflection
- User profile memory
- Project memory
- Knowledge persistence

---

## Phase 13.6 — User Experience

**Objective:** Build the interface through which users interact with KORA.

**Status:** 📋 Planned

### Potential deliverables

- Open WebUI
- Hermes UI
- Chat interface
- Council visualization
- Conversation history
- Explainability
- Decision transparency

---

## Success Criteria

Phase 13 is considered complete when:

- KORA operates as the primary AI interface.
- The Council architecture is fully implemented.
- Memory is persistent.
- Knowledge retrieval is operational.
- External MCP integrations function reliably.
- AI orchestration is modular and maintainable.
- The platform can reason over both user knowledge and homelab infrastructure while preserving the governance standards established during Phases 1–12.

---

## Implementation Notes

This roadmap is expected to evolve significantly during implementation.

It should serve as the authoritative planning document for Phase 13 while remaining consistent with the repository's governance standards.

### Constraints carried forward from Phase 12

- Treat `Documentation/Phase12.5/Production_Baseline.md` as the starting production state unless an explicit change updates it.
- Do not re-litigate media networking or Monarch appdata conventions as part of AI platform design unless a dedicated change is approved.
- Approved remaining debt and deferred work remain tracked under `Documentation/Phase12.5/` and are out of scope for Phase 13 unless intentionally scheduled.

### Documentation expectations

- Prefer architecture and ADRs before irreversible runtime choices.
- Keep Phase 13 tracking artifacts under `Documentation/Phase13/`.
- Keep Council and AI architecture specs under `Architecture/ai/` (and related standards/ADRs as required).
