# Phase 13.4 — Tool Architecture Model

**Status:** ✅ Complete (2026-08-01)  
**Scope:** Architecture and specification only (no MCP installs, Docker changes, API wiring, or tool deployments)

---

## Objective

Define how KORA safely interacts with systems outside itself:

- What tools are
- How they differ from Knowledge, Memory, Agents, and Council
- Lifecycle, permissions, safety, and truth model
- Conceptual MCP role as a future integration protocol

---

## Completed

### Documents created

| Document | Purpose |
| --- | --- |
| `Architecture/ai/Tools.md` | Canonical Tool Architecture |
| `Documentation/Phase13/Tool_Architecture_Model.md` | This report |

### Documents updated / expanded

| Document | Change |
| --- | --- |
| `Architecture/ai/MCP.md` | Expanded conceptual MCP protocol architecture |
| `Architecture/ai/KORA.md` | Tool relationship, principles, document map |
| `Architecture/ai/Agents.md` | Tool relationship and document map |
| `Architecture/ai/README.md` | Tools/MCP entry points and separation rules |
| `Architecture/ai/FuturePlans.md` | 13.4 marked complete |
| `Documentation/Phase13/Phase13_Roadmap.md` | Phase 13.4 complete |
| `Documentation/Phase13/README.md` | Link + status |
| `Architecture/standards/StandardsRoadmap.md` | Phase 13.4 status aligned |

---

## Architectural decisions

### Tool boundaries

- Tools are capability/access — **not intelligence**.
- Tools provide evidence (“what is true right now”), not decisions.
- Knowledge ≠ Tools; Memory ≠ Tools; Agents ≠ Tools; Council ≠ Tools.

### Permission model

Conceptual levels: **Read → Analyze → Propose → Execute → Administrative**

- Default: Read
- Execute/Administrative require authorization / human approval paths
- Audit expectations for Analyze+

### MCP role

- MCP is a **conceptual protocol family** for discovering and exposing tools.
- Defines discovery, capability contracts, permission floors, and security concerns.
- **No implementation or server selection** in this phase.

### Safety principles

- Before / during / after execution checks
- Fail closed for high-impact actions
- Results update Memory/Knowledge only through governance
- Respect Phase 12 production baseline

### Relationship model

`KORA → Council Reasoning → Agent Delegation → Tool Layer → External Environment`

---

## Deferred

| Item | Why deferred |
| --- | --- |
| MCP server deployment / install | Explicitly out of scope |
| API integrations / auth implementation | Implementation track |
| Tool runtime / Docker services | Explicitly out of scope |
| Automation workflows | Later phases |
| Vendor/product selection | Requires ADR |
| Credential wiring | Operational implementation |

---

## Consistency checklist

| Requirement | Status |
| --- | --- |
| Tools ≠ decisions | Explicit |
| Aligns with Agents.md permissions | Explicit |
| No contradiction of Council/Knowledge/Memory | Explicit |
| No deployments | Honored |

---

## Next Phase recommendation

**Recommended next step: Phase 13.5 — Knowledge & Memory Runtime**

### Dependency rationale

1. Tool architecture defines live evidence; durable stores still lack runtime/governance depth.
2. Context assembly needs Memory/Knowledge runtime contracts before UX (13.6) can show provenance well.
3. MCP implementations (later) should write into governed Memory/Knowledge paths defined in 13.5—not invent them.
4. Agent/tool layers are sufficiently specified to avoid redefining them during runtime design.

### Caution for 13.5

Remain architecture-first: define runtime responsibilities and governance without selecting vector DBs, embedding vendors, or deploying stores unless a later explicit implementation phase authorizes it.
