# Phase 13.3 — Agent Architecture Model

**Status:** ✅ Complete (2026-08-01)  
**Scope:** Architecture and specification only (no frameworks, deployments, workflows, or autonomous workers)

---

## Objective

Define when KORA creates or uses agents, how agents differ from Council members, and how temporary execution operates without losing governance.

Primary anti-pattern prevented:

**Council Member = Agent** (forbidden)

---

## Completed

### Documents created / replaced

| Document | Purpose |
| --- | --- |
| `Architecture/ai/Agents.md` | Canonical Agent Orchestration Architecture |
| `Documentation/Phase13/Agent_Architecture_Model.md` | This report |

### Documents updated

| Document | Change |
| --- | --- |
| `Architecture/ai/KORA.md` | Agents subsystem diagram, Council ≠ Agents principle, relationship table |
| `Architecture/ai/README.md` | Conceptual model includes Agents; separation and index updated |
| `Architecture/ai/FuturePlans.md` | 13.3 marked complete |
| `Documentation/Phase13/Phase13_Roadmap.md` | Phase 13.3 complete |
| `Documentation/Phase13/README.md` | Link + status |
| `Architecture/standards/StandardsRoadmap.md` | Phase 13.3 status aligned |

---

## Architectural decisions

### Boundaries

- Council members = durable reasoning perspectives (judgment).
- Agents = temporary execution capability (do work).
- Agents terminate after evaluation; they are not personalities or staff.
- Agents do not override Council, own permanent Memory, or silently mutate authoritative Knowledge.

### Lifecycle

`Need → Determine → Create → Context → Execute → Return → Evaluate → Terminate`

### Creation rules

- Create for large research, audits, scoped execution/drafting.
- Do not create for simple questions or pure judgment decisions (use Council).
- Minimum viable automation: no theatrical agents.

### Permissions (conceptual)

Read-only → Analysis → Proposal → Execution → Administrative  

Default low; higher levels never grant Council override.

### Types (labels only)

Research, Analysis, Maintenance, Documentation, Monitoring, Automation — not Council seats.

### Relationship model

KORA owns delegation. Council reasons. Agents execute via Tools into Environment. Knowledge/Memory receive durable results only through governance after KORA evaluation.

---

## Deferred

| Item | Why deferred |
| --- | --- |
| LangGraph / Hermes / orchestration product choice | Tech selection forbidden |
| Deployed agent services | Out of scope |
| Workflow implementations | Out of scope |
| Runtime sandboxing / queues / retries | Implementation |
| Prompt packs per agent type | Later implementation |
| MCP wiring depth | Phase 13.4 |
| Memory/knowledge runtime stores | Phase 13.5 |

---

## Consistency checklist

| Requirement | Status |
| --- | --- |
| Council ≠ Agents | Explicit |
| KORA creates/evaluates/terminates agents | Explicit |
| No framework selection | Honored |
| No autonomous permanent workers | Honored |
| Aligns with Knowledge/Memory governance | Explicit |

---

## Next Phase recommendation

**Recommended next step: Phase 13.4 — External Integrations**

### Dependency rationale

1. Agents are defined as tool consumers; MCP/tool architecture is the next missing contract.
2. Without tool boundaries, Execution/Administrative permission levels cannot be made real later.
3. Phase 13.5 runtime memory/knowledge benefits from knowing which live facts come from tools vs durable stores.
4. Council and Knowledge architectures are sufficiently complete to avoid redefining them during MCP design.

### Caution for 13.4

Specify MCP/tool permissions and safety as architecture only—still no deployments unless a later phase explicitly authorizes them.
