# KORA Implementation Architecture Framework

**Status:** Canonical implementation-planning framework (Phase 13.7)  
**Platform:** KORA / Brainiac (`KORA.md`)  
**Rule:** Technology must satisfy architecture. Architecture must not be rewritten to fit a tool.

Phase 13.0–13.6 defined **what KORA must be**.  
Phase 13.7 defines **how implementation decisions will be evaluated** before anything is built.

This phase does **not** deploy software, install services, modify Docker, or select technologies as final.

---

## Purpose

Answer:

> How do we choose technology without allowing technology to redefine KORA?

Implementation planning must:

1. Map every runtime component to an existing architectural concern
2. Evaluate candidates against architecture fit, not hype
3. Preserve replaceability (no irreversible lock-in by default)
4. Require ADRs for technology selections
5. Sequence work so governance and contracts stay intact

---

## Implementation Layers

```text
┌─────────────────────────────────────────────┐
│           User Interface Layer              │
│     (chat / future voice / mobile / UX)     │
└────────────────────┬────────────────────────┘
                     │
┌────────────────────▼────────────────────────┐
│        KORA Orchestration Layer             │
│  classify · select · assemble · synthesize  │
│           governance enforcement            │
└──────┬─────────────┬─────────────┬──────────┘
       │             │             │
┌──────▼──────┐ ┌────▼─────┐ ┌─────▼──────┐
│ Memory      │ │ Knowledge│ │ Agents     │
│ Runtime     │ │ Runtime  │ │ + Tools    │
└─────────────┘ └────┬─────┘ └─────┬──────┘
                     │             │
              ┌──────▼─────────────▼──────┐
              │ Relationship Knowledge    │
              │ (optional graph layer)    │
              └───────────────────────────┘
                     │
              ┌──────▼────────────────────┐
              │ External Environment      │
              │ (homelab systems via MCP) │
              └───────────────────────────┘
```

Layers are **service boundaries in principle**, not a mandate to deploy one container per box tomorrow.

---

## Service Boundaries (Conceptual)

| Layer | Implements | Must not become |
| --- | --- | --- |
| **User Interface** | `User_Experience.md`, `Interaction_Model.md`, `Explainability.md` | A second “assistant” identity replacing KORA |
| **KORA Orchestration** | `KORA.md`, Council Selection/Deliberation/Voting, Context Assembly | A generic agent framework that erases Council |
| **Memory Runtime** | `Memory.md`, `Memory_Runtime.md` | A dump of chat logs treated as Knowledge |
| **Knowledge Runtime** | `Knowledge.md`, `Knowledge_Runtime.md` | Un governed scrapings without provenance |
| **Relationship Knowledge** | Conceptual graph requirements in Knowledge Architecture | The sole source of truth replacing documents |
| **Tool Integration** | `Tools.md`, `MCP.md`, Agent tool use | Unaudited admin access / silent Execute |

---

## Architecture Mapping

| Architectural concern | Implementation layer | Candidate(s) — not selected |
| --- | --- | --- |
| User interaction | UI Layer | Open WebUI (evaluate) |
| Orchestration / Council / agents coordination | KORA Orchestration Layer | Hermes (evaluate) |
| Memory lifecycle | Memory Runtime Layer | Honcho (evaluate) |
| Semantic retrieval / knowledge store | Knowledge Runtime Layer | ChromaDB (evaluate) |
| Relationship modeling | Relationship Knowledge Layer | Graphify (evaluate) |
| Live environment capability | Tool Integration Layer | MCP-compatible tools (evaluate later) |
| Inference | Models (cross-cutting) | Deferred; `Models.md` |

Candidates are **evaluation targets only**. Final selection requires ADRs using the criteria below.

---

## Deployment Philosophy

1. **Architecture first, stack second** — No install that forces rewriting Phase 13 contracts.
2. **Thin vertical slices** — Prefer small end-to-end paths (e.g., chat → assemble → recommend → explain) over big-bang platforms.
3. **Replaceability** — Prefer components that can be swapped without renaming KORA or dissolving Council/Memory/Knowledge boundaries.
4. **Homelab baseline respect** — Implementations must honor Phase 12 production baseline and governance standards.
5. **No silent privilege** — Execute/Administrative paths require approval UX and auditability.
6. **Obsidian boundary** — Obsidian is **not** a KORA runtime component. It may be an external markdown creation workflow with optional future ingestion. KORA must not depend on Obsidian to function.
7. **Docs remain SoT for identity** — Runtime code implements docs; docs are not generated as afterthoughts of a vendor tutorial.

---

## Layer Details

### 1. User Interface Layer

**Purpose:** Expose KORA interaction.

Must support (per UX architecture):

- Chat
- Future voice
- Mobile access
- Explainability
- Council visibility modes
- Project interaction
- Memory controls
- Approval flows

**Candidate:** Open WebUI  

Evaluate:

- Hermes compatibility (integrate with orchestration rather than replace KORA)
- Extensibility for explainability/provenance UI
- API support
- Future replacement possibility

**Do not select in this phase.**

---

### 2. KORA Orchestration Layer

**Purpose:** Core intelligence coordination.

Responsibilities:

- Request classification
- Council selection
- Context assembly
- Response synthesis
- Governance enforcement
- Agent create/evaluate/terminate lifecycle

**Candidate:** Hermes  

Evaluate against:

- Council architecture (members ≠ agents)
- Agents architecture
- Tool integration / MCP support
- Memory integration
- Ability to preserve KORA as product identity

**Do not select in this phase.**

---

### 3. Memory Runtime Layer

**Purpose:** Implement `Memory_Runtime.md`.

Responsibilities:

- User memories / preferences
- Project continuity
- Correction / deletion / approval
- Expiration
- Provenance of remembered items

**Preferred candidate for evaluation:** Honcho  

Evaluate against:

- Memory governance
- User control
- Provenance
- Lifecycle management
- Clear separation from Knowledge stores

**Do not select in this phase.**

---

### 4. Knowledge Runtime Layer

**Purpose:** Implement `Knowledge_Runtime.md` retrieval/store aspects.

Responsibilities:

- Document knowledge indexing/retrieval
- Semantic retrieval (when implemented)
- Source authority metadata
- Freshness metadata
- Provenance

**Candidate:** ChromaDB  

Evaluate against:

- Retrieval requirements
- Scalability for homelab corpus
- Metadata support for authority/freshness/provenance
- Migration/export ability

**Do not select in this phase.**

---

### 5. Relationship Knowledge Layer

**Purpose:** Represent relationships among services, projects, docs, decisions, infrastructure, and concepts.

**Candidate:** Graphify  
**Source:** https://github.com/Graphify-Labs/graphify  

Evaluate against:

- Relationship modeling needs from Knowledge Architecture
- Project awareness UX
- Architecture discovery value
- Whether it complements (not replaces) document SoT

**Do not select in this phase.**

---

### 6. Tool Integration Layer

**Purpose:** Implement `Tools.md` / `MCP.md`.

Responsibilities:

- MCP compatibility (conceptual → later concrete)
- External / homelab system access
- Controlled execution
- Permissions, audit, approval workflows

Evaluate:

- Security
- Permissions mapping (Read→Administrative)
- Auditability
- Approval workflows
- Blast radius / least privilege

**Do not install MCP servers in this phase.**

---

## Technology Evaluation Methodology

Every candidate technology must be scored against the following dimensions before an ADR decision.

### Architecture Fit

Does it satisfy:

- `KORA.md`
- Council model
- Knowledge model
- Memory model
- Agents / Tools models
- UX / Explainability models

Reject candidates that require erasing Council≠Agents, Memory≠Knowledge, or Tools≠Decisions.

### Maintainability

Evaluate:

- Complexity
- Operational burden
- Documentation quality
- Community health
- Long-term viability

### Integration

Evaluate:

- APIs
- Interoperability
- Standards support (including MCP where relevant)
- Replacement possibility

### Governance

Evaluate:

- Permissions
- Auditability
- Data ownership (who holds the bits; can we export?)
- Migration ability

### Additional recommended dimensions

| Dimension | Questions |
| --- | --- |
| **Security** | Authn/z, secrets, exposure, failure modes |
| **Performance** | Adequate for homelab scale? Failure under load? |
| **Operational complexity** | Backups, upgrades, observability burden |
| **Community** | Stewardship, release cadence, abandonment risk |
| **Migration** | Exit cost if we leave |

### Decision outcomes

Each evaluation ADR should conclude with one of:

- **Adopt (provisional)** — with constraints and rollback plan
- **Defer** — missing evidence / not needed yet
- **Reject** — architecture mismatch or unacceptable risk
- **Spike** — time-boxed experiment with explicit non-production limits

Reusable template: `Technology_Evaluation_ADR_Template.md`.

---

## Preferred Candidate Technologies (Evaluation Only)

| Candidate | Potential role | Status |
| --- | --- | --- |
| Honcho | Memory Runtime | Candidate — not selected |
| Graphify | Relationship / graph knowledge | Candidate — not selected |
| ChromaDB | Semantic retrieval / knowledge store | Candidate — not selected |
| Hermes | Orchestration / agent coordination | Candidate — not selected |
| Open WebUI | UI layer | Candidate — not selected; must not replace Hermes/KORA |

### Obsidian boundary

Obsidian is **not** a KORA runtime component.

Treat as:

- External user knowledge creation workflow

Possible future integrations:

- Markdown ingestion
- Project documentation import

**Do not make KORA dependent on Obsidian.**

---

## Implementation Sequencing (Recommended)

1. **Evaluation ADRs** for UI, Orchestration, Memory, Knowledge (order may parallelize, decisions must not conflict)
2. **Thin vertical slice:** UI → Orchestration → Context Assembly (even if Memory/Knowledge start as repo-backed stubs)
3. **Explainability + Council visibility modes** in the UI contract
4. **Memory runtime** with user controls
5. **Knowledge runtime** with provenance metadata
6. **Relationship layer** if discovery value is proven
7. **Tool/MCP integrations** with Read-first permissions
8. **Agent execution** only after tool permission/audit paths exist

Never start with unbounded automation.

---

## Non-goals (Phase 13.7)

- Deploying any of the candidates
- Modifying Docker / compose
- Installing MCP servers
- Beginning feature implementation
- Declaring final technology winners without ADRs

---

## Document Map

| Document | Role |
| --- | --- |
| `Implementation_Architecture.md` (this file) | Implementation framework & evaluation method |
| `Technology_Evaluation_ADR_Template.md` | Reusable ADR criteria for tech choices |
| `Documentation/Phase13/Implementation_Architecture_Model.md` | Phase 13.7 report |
| Phase 13.0–13.6 docs | Binding architectural contracts |
