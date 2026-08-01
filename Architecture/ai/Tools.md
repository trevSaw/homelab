# Tool Architecture

**Status:** Canonical architecture specification (Phase 13.4)  
**Platform:** KORA / Brainiac (`KORA.md`)  
**Protocol companion:** `MCP.md` (conceptual integration protocol — not an implementation choice)

Tools answer: **What can KORA interact with?** / **What is true right now?**  
Tools do **not** answer: **What should KORA decide?**

---

## Core Principle

**Tools are not intelligence.**

Tools provide capability and access to the external environment.  
Council provides judgment.  
Agents may invoke tools to perform scoped work.  
KORA evaluates results and synthesizes user-facing recommendations.

```text
KORA
  |
Council Reasoning
  |
Agent Delegation
  |
Tool Layer
  |
External Environment
```

---

## Separation of Concerns

| Concern | Answers | Document |
| --- | --- | --- |
| **Knowledge** | What information exists? | `Knowledge.md` |
| **Memory** | What does KORA remember? | `Memory.md` |
| **Tools** | What is true right now? / What can be interacted with? | `Tools.md` (this file) |
| **Agents** | Who performs scoped work? | `Agents.md` |
| **Council** | How should decisions be evaluated? | `Council/` |

### Knowledge vs live tools

| Knowledge | Tools |
| --- | --- |
| Durable reference corpus | Live environment access |
| Docs, standards, ADRs, inventories | Docker status, sensors, git state, APIs |
| Governed freshness/authority | Point-in-time evidence |
| Does not equal “now” | Does not equal “always true later” |

### Agents vs tools

| Agents | Tools |
| --- | --- |
| Temporary workers | Capabilities/interfaces |
| May call tools | Do not reason or decide |
| Have lifecycle (create→terminate) | Have invocation lifecycle (request→result) |
| Evaluated by KORA | Produce evidence for KORA/Council |

---

## Why KORA Needs Tools

- Homelab truth changes; Knowledge alone can be stale.
- Decisions about infrastructure require live evidence (running containers, DNS, sensors).
- Agents need a governed interface to the environment.
- Users deserve recommendations grounded in current state, not only documentation.

Tools enable interaction. They do not replace Council deliberation.

---

## Tool Categories (Conceptual)

No implementations selected.

### Infrastructure Tools

Potential future examples:

- Docker management / inspection
- System monitoring
- Storage inspection
- Network inspection

### Knowledge Tools

Potential future examples:

- Search
- Retrieval
- Document indexing

(These support Knowledge operations; they are still tools—not the Knowledge corpus itself.)

### Productivity Tools

Potential future examples:

- Calendar
- Tasks
- Notifications

### Home Automation Tools

Potential future examples:

- Home Assistant
- Sensors
- Smart devices

### Development Tools

Potential future examples:

- Git
- Code analysis
- Testing systems

### External Information Tools

Potential future examples:

- Web research
- APIs
- External data sources

Categories are planning labels for permission templates and ownership—not product selections.

---

## Tool Lifecycle

```text
Request
  ↓
KORA Determines Capability Needed
  ↓
Permission Evaluation
  ↓
Agent or KORA Invokes Tool
  ↓
Tool Executes
  ↓
Result Validation
  ↓
Context Returned
  ↓
Decision / Recommendation
```

| Stage | Purpose |
| --- | --- |
| **Request** | User need or internal deliberation identifies an environment interaction |
| **KORA Determines Capability Needed** | Map need to tool category/capability; decide if tool use is required at all |
| **Permission Evaluation** | Check conceptual permission level, scope, approval requirements |
| **Agent or KORA Invokes Tool** | Direct invoke (simple) or agent-mediated invoke (scoped labor) |
| **Tool Executes** | Perform the external operation / query |
| **Result Validation** | Check completeness, errors, unexpected side effects |
| **Context Returned** | Label result as tool evidence with provenance/time |
| **Decision / Recommendation** | Council/KORA judge; tools do not decide |

---

## Tool Permissions Model (Conceptual)

Aligned with agent permission philosophy; tools enforce capability ceilings.

| Level | Intent | Examples |
| --- | --- | --- |
| **Read** | Inspect information | View Docker status, read files, query sensors |
| **Analyze** | Process information | Generate reports, compare states |
| **Propose** | Prepare changes | Draft configuration, suggest remediation |
| **Execute** | Perform approved changes | Restart service, modify configuration |
| **Administrative** | Highest risk | Infrastructure changes, destructive actions |

### Defaults

- Default tool access: **Read**
- **Analyze** requires explicit task need
- **Propose** produces drafts only—never silent authoritative publish
- **Execute** requires explicit authorization path (human and/or prior approved charter)
- **Administrative** requires human approval; never implied by conversation tone

### Approval requirements

| Level | Approval expectation |
| --- | --- |
| Read / Analyze | Generally allowable within KORA session governance |
| Propose | Results reviewed by KORA/Council/human before treated as approved action |
| Execute | Pre-authorized scope or explicit approval |
| Administrative | Explicit human approval; auditable |

### Audit requirements

Every non-trivial tool invocation should be able to record (conceptually):

- Who/what initiated (KORA or which agent)
- Tool identity and capability
- Permission level used
- Scope/parameters (sanitized)
- Outcome / error
- Timestamp

---

## Safety Model

### Before execution

- Is the tool required?
- Is the request authorized at the needed permission level?
- Is scope understood and bounded?
- Is rollback possible if Execute/Administrative?
- Does Phase 12 baseline / change-control apply?

### During execution

- Preserve audit trail
- Capture outputs and errors
- Fail closed on ambiguity for Execute/Administrative
- Do not expand scope mid-run without re-authorization

### After execution

- Verify outcome against intent
- Return evidence to context with provenance
- Update Memory/Knowledge **only through governance** (`Memory_Runtime.md`, `Knowledge_Runtime.md`)—never silent authoritative mutation from raw tool output
- Surface failures honestly to the user/Council

---

## Tool Truth Model

**Tools provide evidence, not decisions.**

Example:

- Tool: “Container is stopped.”
- Council/KORA: “What should be done?”

Rules:

1. Tool output is point-in-time evidence.
2. Conflicting tool vs Knowledge results must be surfaced (freshness/authority conflict).
3. Tool success ≠ recommendation correctness.
4. Absence of tool access ≠ permission to invent live state.
5. Epistemic labeling: evidence from tools should remain distinguishable from Knowledge and Memory.

---

## Relationship Model

```text
             KORA
               |
      Council Reasoning
               |
    Agent Delegation Layer
               |
         Tool Layer
               |
    External Environment
```

| Relationship | Rule |
| --- | --- |
| **KORA → Tools** | Decides need, evaluates permissions, may invoke directly |
| **Agents → Tools** | Invoke only within agent charter + tool permission ceiling |
| **Council → Tools** | May request live evidence via KORA; does not become a tool user identity |
| **Tools → Council** | Supply evidence for judgment |
| **Tools → Knowledge** | May feed candidates for governance promotion; not automatic Knowledge writes |
| **Tools → Memory** | May inform what happened; durable Memory writes go through KORA evaluation |
| **MCP → Tools** | Preferred future protocol family for exposing capabilities (see `MCP.md`) |

---

## Tool Governance

| Concern | Rule |
| --- | --- |
| **Ownership** | Each tool/capability has a clear owner (platform role / doc path) |
| **Versioning** | Tool contracts version conceptually; breaking capability changes require review |
| **Deprecation** | Deprecated tools must not remain default; replacements documented |
| **Auditability** | Invocations at Analyze+ should be reconstructable |
| **Trust levels** | Built-in/homelab tools ≠ arbitrary external APIs; trust affects default permission |
| **Human approval boundaries** | Execute/Administrative and authoritative Knowledge promotion remain human-gated as required |

Homelab tool use must respect `Documentation/Phase12.5/Production_Baseline.md` and existing governance standards.

---

## Future Implementation Boundaries

Not authorized by this document alone:

- Installing MCP servers
- Docker Compose for tool runtimes
- API credential wiring
- Automation platforms
- Vendor/product selection
- Production tool code

Those require later implementation phases and ADRs where technology is chosen.

---

## Document Map

| Document | Role |
| --- | --- |
| `Tools.md` (this file) | Canonical Tool Architecture |
| `MCP.md` | Conceptual MCP protocol architecture |
| `Agents.md` | Who may invoke tools for scoped work |
| `Knowledge.md` / `Knowledge_Runtime.md` | Non-live reference stores |
| `Memory.md` / `Memory_Runtime.md` | Continuity stores |
| `Context_Assembly.md` | How tool evidence enters reasoning context |
| `Council/` | Decision evaluation |
| `Documentation/Phase13/Tool_Architecture_Model.md` | Phase 13.4 report |

---

## Status

Phase 13.4 architecture complete at the conceptual level.  
No tool deployments or MCP installations are authorized by this document alone.
