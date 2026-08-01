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
| 13.0 | KORA Architecture Alignment | ✅ Complete (2026-08-01) |
| 13.1 | Council Architecture | ✅ Complete (2026-08-01) |
| 13.2 | Knowledge Architecture | ✅ Complete (2026-08-01) |
| 13.3 | Agent Orchestration | ✅ Complete (2026-08-01) |
| 13.4 | External Integrations | ✅ Complete (2026-08-01) |
| 13.5 | Knowledge & Memory Runtime | ✅ Complete (2026-08-01) |
| 13.6 | User Experience | ✅ Complete (2026-08-01) |
| 13.7 | Implementation Architecture Framework | ✅ Complete (2026-08-01) |
| 13.8 | Technology Evaluation & Adoption ADRs | ✅ Complete (2026-08-01) |
| 13.9 | KORA Thin Vertical Slice Architecture | ✅ Complete (2026-08-01) |
| 13.10 | KORA Prototype Spike Architecture | ✅ Complete (2026-08-01) |

---

## Phase 13.0 — KORA Architecture Alignment

**Objective:** Align AI architecture documentation to the finalized model: KORA is Brainiac; KORA is Council Chair/Conductor and a Council member; subsystems separate cleanly.

**Status:** ✅ Complete (2026-08-01)

### Deliverables

- `Architecture/ai/KORA.md`
- Updated `Architecture/ai/README.md`
- Consistency updates to Council entry docs and subsystem stubs
- `Documentation/Phase13/KORA_Architecture_Alignment.md`

---

## Phase 13.1 — Council Architecture

**Objective:** Define the Council as the reasoning framework used by KORA, including operational selection, deliberation, and synthesis mechanics.

**Status:** ✅ Complete (2026-08-01)

### Deliverables

- Council directory structure
- Council architecture
- Dynamics.md
- Member specifications
- Selection rules
- Voting / deliberative synthesis rules
- Deliberation lifecycle
- Prompt architecture (conceptual)
- Conceptual schemas
- Canonical member template

### Working tree

Primary artifacts live under `Architecture/ai/Council/`.

Phase report: `Documentation/Phase13/Council_Operational_Model.md`

---

## Phase 13.2 — Knowledge Architecture

**Objective:** Design how KORA organizes, retrieves, governs, and supplies reference information to Council reasoning—without selecting databases or RAG stacks.

**Status:** ✅ Complete (2026-08-01)

### Deliverables

- `Architecture/ai/Knowledge.md`
- Knowledge domains, lifecycle, quality, retrieval, governance, and conceptual relationships
- Memory ≠ Knowledge boundary clarified in `Memory.md` and `KORA.md`
- Phase report: `Documentation/Phase13/Knowledge_Architecture_Model.md`

### Note on roadmap wording

Earlier draft deliverables mixed memory runtime items into 13.2. Those runtime items remain **Phase 13.5**. Phase 13.2 defines Knowledge Architecture and clarifies Memory boundaries only.

---

## Phase 13.3 — Agent Orchestration

**Objective:** Define how KORA delegates temporary execution work through agents—without conflating agents with Council members or selecting frameworks.

**Status:** ✅ Complete (2026-08-01)

### Deliverables

- `Architecture/ai/Agents.md` — lifecycle, creation rules, boundaries, permissions, types
- Explicit **Council ≠ Agents** architecture
- Phase report: `Documentation/Phase13/Agent_Architecture_Model.md`

### Note on earlier roadmap wording

Earlier draft listed Hermes integration, prompt assembly, and conversation management as 13.3 deliverables. Those remain **implementation concerns** for later tracks. Phase 13.3 locks the agent governance model first.

---

## Phase 13.4 — External Integrations

**Objective:** Define how KORA safely interacts with the external world through a governed tool layer (including conceptual MCP), without deploying integrations.

**Status:** ✅ Complete (2026-08-01)

### Deliverables

- `Architecture/ai/Tools.md`
- Expanded `Architecture/ai/MCP.md`
- Tool lifecycle, permissions, safety, truth model, governance
- Phase report: `Documentation/Phase13/Tool_Architecture_Model.md`

### Note on earlier roadmap wording

Earlier draft listed concrete MCP servers (Filesystem, Git, Docker, Home Assistant, Technitium) as deliverables. Those remain **future implementation candidates** under this architecture—not Phase 13.4 deployment work.

---

## Phase 13.5 — Knowledge & Memory Runtime

**Objective:** Define how KORA maintains continuity, evolves knowledge, and assembles provenance-labeled context—without selecting databases or deploying runtimes.

**Status:** ✅ Complete (2026-08-01)

### Deliverables

- `Architecture/ai/Memory_Runtime.md`
- `Architecture/ai/Knowledge_Runtime.md`
- `Architecture/ai/Context_Assembly.md`
- Memory lifecycle and user-control governance
- Knowledge promotion pipeline (Candidate → Authoritative)
- Context assembly priority, conflict, and provenance rules
- Phase report: `Documentation/Phase13/Memory_Runtime_Model.md`

### Note on earlier roadmap wording

Earlier draft listed production memory implementation items (semantic retrieval, persistence services). Those remain **future implementation** under this architecture—not Phase 13.5 deployment work.

---

## Phase 13.6 — User Experience

**Objective:** Define how humans interact with KORA—trust, transparency, interaction patterns, and explainability—without selecting UI frameworks or clients.

**Status:** ✅ Complete (2026-08-01)

### Deliverables

- `Architecture/ai/User_Experience.md`
- `Architecture/ai/Interaction_Model.md`
- `Architecture/ai/Explainability.md`
- Council visibility modes (Invisible / Advisory / Full)
- Memory/knowledge/project/task UX contracts
- Phase report: `Documentation/Phase13/User_Experience_Model.md`

### Note on earlier roadmap wording

Earlier draft listed concrete clients (Open WebUI, Hermes UI). Those remain **future implementation candidates** under this UX contract—not Phase 13.6 product selections.

---

## Phase 13.7 — Implementation Architecture Framework

**Objective:** Define how future implementation decisions will be evaluated so technology cannot redefine KORA.

**Status:** ✅ Complete (2026-08-01)

### Deliverables

- `Architecture/ai/Implementation_Architecture.md`
- `Architecture/ai/Technology_Evaluation_ADR_Template.md`
- Implementation layers, deployment philosophy, evaluation methodology, sequencing
- Candidate list explicitly marked not-selected (Honcho, Graphify, ChromaDB, Hermes, Open WebUI)
- Obsidian boundary (external workflow, not runtime dependency)
- Phase report: `Documentation/Phase13/Implementation_Architecture_Model.md`

---

## Phase 13.8 — Technology Evaluation & Adoption ADRs

**Objective:** Evaluate first-wave technology candidates against KORA architecture contracts. Determine fit and adoption posture—not install services.

**Status:** ✅ Complete (2026-08-01)

### Deliverables

- `Architecture/decisions/ADR-0004-KORA-Orchestration-Hermes.md` — Provisional Adopt
- `Architecture/decisions/ADR-0005-Memory-Runtime-Honcho.md` — Spike
- `Architecture/decisions/ADR-0006-Knowledge-Retrieval-ChromaDB.md` — Provisional Adopt
- `Architecture/decisions/ADR-0007-Relationship-Layer-Graphify.md` — Defer
- `Architecture/decisions/ADR-0008-User-Interface-OpenWebUI.md` — Provisional Adopt
- Updated `Architecture/decisions/ADRIndex.md`
- Phase report: `Documentation/Phase13/Technology_Evaluation_ADR_Model.md`

### Explicit non-deliverables

No Docker services, compose files, deployments, or final production stack selection.

---

## Phase 13.9 — KORA Thin Vertical Slice Architecture

**Objective:** Validate Phase 13 architecture through a minimal end-to-end prototype design. Architecture validation only—no installs or compose.

**Status:** ✅ Complete (2026-08-01)

### Deliverables

- `Architecture/ai/Vertical_Slice.md`
- `Architecture/ai/Prototype_Boundaries.md`
- `Architecture/ai/Integration_Flow.md`
- Phase report: `Documentation/Phase13/Vertical_Slice_Model.md`

### Explicit non-deliverables

No Docker services, compose files, deployments, or installs of Hermes / Open WebUI / Honcho / ChromaDB / Graphify.

---

## Phase 13.10 — KORA Prototype Spike Architecture

**Objective:** Define the first controlled non-production spike (planning only) for validating KORA architectural assumptions.

**Status:** ✅ Complete (2026-08-01)

### Deliverables

- `Architecture/ai/Spike_Architecture.md`
- `Architecture/ai/Spike_Acceptance_Criteria.md`
- `Architecture/ai/Spike_Test_Plan.md`
- Phase report: `Documentation/Phase13/Prototype_Spike_Model.md`

### Explicit non-deliverables

No runtime execution, Docker compose, production deployment, permanent Memory writes, MCP execution, or infrastructure changes.

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
