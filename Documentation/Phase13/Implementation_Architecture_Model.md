# Phase 13.7 — Implementation Architecture Model

**Status:** ✅ Complete (2026-08-01)  
**Scope:** Implementation-planning framework only (no deploys, installs, compose, or final tech selection)

---

## Objectives

Bridge architecture and implementation by defining:

- Implementation layers and service boundaries
- Mapping from Phase 13.0–13.6 concerns to runtime layers
- Deployment philosophy
- Technology evaluation methodology
- Candidate list (explicitly not selected)
- Sequencing guidance and Obsidian boundary

---

## Completed

### Documents created

| Document | Purpose |
| --- | --- |
| `Architecture/ai/Implementation_Architecture.md` | Implementation architecture framework |
| `Architecture/ai/Technology_Evaluation_ADR_Template.md` | Reusable tech-evaluation ADR criteria |
| `Documentation/Phase13/Implementation_Architecture_Model.md` | This report |

### Documents updated

| Document | Change |
| --- | --- |
| `Architecture/ai/KORA.md` | Implementation framework pointers; future evolution |
| `Architecture/ai/README.md` | Index + implementation planning entry |
| `Architecture/ai/FuturePlans.md` | 13.7 complete; next = evaluation ADRs |
| `Documentation/Phase13/Phase13_Roadmap.md` | Phase 13.7 added/complete |
| `Documentation/Phase13/README.md` | Link + status |
| `Architecture/standards/StandardsRoadmap.md` | Phase 13.7 entry |

---

## Architectural decisions

1. **Technology must fit KORA architecture; architecture is not rewritten for a tool.**
2. **Six implementation layers:** UI, Orchestration, Memory Runtime, Knowledge Runtime, Relationship Knowledge, Tool Integration.
3. **Candidates only (not selected):** Open WebUI, Hermes, Honcho, ChromaDB, Graphify.
4. **Open WebUI must be evaluated as UI integrating with orchestration—not as a replacement for KORA/Hermes identity.**
5. **Obsidian is external workflow, not a KORA runtime dependency.**
6. **All selections require ADRs** using Architecture Fit, Security, Maintenance, Integration, Performance, Migration, Community, Operational Complexity, Governance, Decision.
7. **Sequencing:** evaluate → thin vertical slice → memory/knowledge → tools/agents; no unbounded automation first.

---

## Deferred

| Item | Why deferred |
| --- | --- |
| Final technology selection | Requires ADRs / spikes |
| Docker / compose / installs | Explicitly out of scope |
| MCP server deployment | Later implementation |
| Production cutovers | Later implementation |
| Obsidian ingestion | Optional future integration |

---

## Consistency checks

| Requirement | Status |
| --- | --- |
| Does not contradict 13.0–13.6 | Explicit mapping |
| Does not select tech as final | Candidates labeled |
| Prevents Council≠Agents / Memory≠Knowledge collapse | Architecture Fit gate |
| Working-tree commit scoped to 13.7 | Required at git step |

---

## Next steps recommendation

**Recommended next phase: Technology Evaluation ADRs (first wave)**

Suggested first ADRs (parallelizable):

1. UI candidate evaluation (Open WebUI vs alternatives) against UX/Explainability
2. Orchestration candidate evaluation (Hermes) against Council/Agents/Tools
3. Memory candidate evaluation (Honcho) against Memory_Runtime
4. Knowledge retrieval candidate evaluation (ChromaDB) against Knowledge_Runtime

Only after provisional Adopt decisions: authorize a thin non-production spike with explicit rollback.
