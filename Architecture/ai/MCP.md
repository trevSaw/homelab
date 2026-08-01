# MCP Architecture (Conceptual)

**Status:** Canonical protocol architecture specification (Phase 13.4)  
**Companion:** `Tools.md` (tool layer behavior, permissions, safety)  
**Platform:** KORA / Brainiac (`KORA.md`)

MCP (Model Context Protocol) is treated here as a **future integration protocol family** for exposing tools to KORA—not as a selected product deployment.

This document defines architectural requirements MCP-style integrations must satisfy.  
It does **not** install servers, choose SDKs, or create configurations.

---

## Role in the KORA architecture

```text
KORA
  |
Council Reasoning
  |
Agent Delegation
  |
Tool Layer  ←── MCP exposes capabilities into this layer
  |
External Environment
```

| MCP / tools provide | MCP / tools do not provide |
| --- | --- |
| Bounded access to external systems | Platform identity (KORA / Brainiac) |
| Discoverable capabilities with schemas | Council deliberation or final decisions |
| Permission-applicable operations | Replacement for Knowledge/Memory |
| Live evidence and controlled actions | Autonomous governance override |

**Tools are not intelligence.** MCP is a way to offer tools consistently.

---

## Why a protocol layer

Without a protocol contract, integrations tend to become ad hoc scripts with uneven safety. A conceptual MCP layer provides:

1. **Tool discovery** — what capabilities exist
2. **Capability exposure** — typed operations and inputs/outputs
3. **Permission boundaries** — map operations to Read→Administrative ceilings
4. **Security considerations** — authn/z, least privilege, audit hooks
5. **Uniform invocation** — KORA/agents call through one architectural pattern

---

## Tool Discovery (Conceptual)

Discovery should answer:

- Which tools/servers are available?
- Which capabilities does each expose?
- What permission level does each capability require (minimum)?
- What environment/domain does it touch (infra, HA, git, …)?
- What is its trust level (homelab-built-in vs external)?

Discovery results feed KORA’s “capability needed” decision in the tool lifecycle (`Tools.md`).

---

## Capability Exposure (Conceptual)

Each capability should declare (conceptually):

| Field | Meaning |
| --- | --- |
| Identity | Stable capability name |
| Description | Human/KORA-readable purpose |
| Category | Infrastructure, Knowledge, Productivity, Home Automation, Development, External, … |
| Permission floor | Minimum permission level to invoke |
| Side effects | none / read / write / destructive |
| Rollback notes | Whether/how reversal is possible |
| Input/output contract | Expected arguments and result shape |
| Audit class | Whether invocation must be recorded |

Capabilities with write/destructive side effects cannot default to Read.

---

## Permission Boundaries

MCP integrations must honor `Tools.md` permission model:

- Read
- Analyze
- Propose
- Execute
- Administrative

Rules:

1. Protocol exposure must not silently elevate privilege.
2. Agent charters cannot exceed the tool capability’s permission floor without approval path.
3. Administrative capabilities require human approval gates architecturally.
4. Missing permission metadata ⇒ treat as highest plausible risk until classified (fail closed for Execute+).

---

## Security Considerations (Conceptual)

Required architectural concerns for any future MCP deployment:

| Concern | Requirement |
| --- | --- |
| Authentication | Callers/tools mutually identified |
| Authorization | Least privilege per capability |
| Secret handling | No secrets in Knowledge/Memory dumps or logs |
| Network exposure | Prefer internal-only endpoints; no casual public tool surfaces |
| Supply trust | External MCP servers are lower trust by default |
| Sandbox blast radius | Tool compromise must not equal full host admin by default |
| Audit | Reconstructable invocation history for Analyze+ where feasible |
| Baseline conformance | Respect Phase 12 production baseline and change control |

No concrete IdP, secret store, or network product is selected here.

---

## Relationship to Agents and Council

- **Council** may request live evidence; it does not own MCP connections.
- **Agents** invoke MCP-exposed tools within charter + permission ceiling.
- **KORA** decides necessity, evaluates results, synthesizes recommendations.
- MCP output is **evidence** for deliberation—not a decision.

---

## Governance

| Topic | Rule |
| --- | --- |
| Ownership | Each MCP server/capability has an owner |
| Versioning | Capability contract changes are reviewed |
| Deprecation | Removed/disabled tools must not remain discoverable as healthy defaults |
| Inventory | Conceptual registry of allowed integrations (future implementation) |
| Human approval | Required for adding Execute/Administrative capabilities to the allowed set |

---

## Non-goals (Phase 13.4)

Do not:

- Select or install an MCP implementation
- Create MCP server configs
- Deploy MCP sidecars/services
- Wire production credentials
- Treat “MCP” as synonymous with a specific vendor stack without an ADR

---

## Document Map

| Document | Role |
| --- | --- |
| `MCP.md` (this file) | Protocol/integration architecture |
| `Tools.md` | Tool layer behavior, lifecycle, safety, permissions |
| `Agents.md` | Delegation that may call tools |
| `Documentation/Phase13/Tool_Architecture_Model.md` | Phase 13.4 report |

---

## Status

Conceptual MCP architecture complete for Phase 13.4.  
Implementation and deployment remain deferred.
