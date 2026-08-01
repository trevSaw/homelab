# Memory Runtime Architecture

**Status:** Canonical runtime architecture specification (Phase 13.5)  
**Boundary companion:** `Memory.md`  
**Platform:** KORA / Brainiac (`KORA.md`)  
**Related:** `Knowledge_Runtime.md`, `Context_Assembly.md`

Memory answers: **What does KORA remember about continuity, interaction, preferences, and prior context?**

This document defines how memory is captured, governed, retrieved, and expired over time.  
It does **not** select databases, embeddings, or memory products.

---

## Memory Purpose

### Why KORA needs memory

- Continuity across sessions without forcing the user to restate everything
- Recall of prior decisions, constraints, and preferences that affect new recommendations
- Operational learning (incidents, lessons) without converting anecdotes into authoritative Knowledge
- Short-lived reasoning state for the active conversation

### Memory ≠ Knowledge

| Memory | Knowledge |
| --- | --- |
| Continuity / interaction history | Validated reference material |
| “What happened with this user/project?” | “What information exists?” |
| User-controlled personal continuity | Governed corpus with authority tiers |
| May be corrected/forgotten by user | Superseded through ownership/governance |

### Memory ≠ Conversation history alone

| Conversation history | Memory |
| --- | --- |
| Raw turn stream of the current/recent chat | Evaluated, classified continuity artifacts |
| Often ephemeral UI/session buffer | May include durable categories after evaluation |
| Not automatically authoritative | Still never silently becomes Knowledge |

Raw conversation may feed Capture; only evaluated items become durable Memory categories.

---

## Memory Categories (Conceptual)

No storage formats selected.

### User Memory

Examples:

- Preferences
- Working style
- Long-term goals

**Control:** User primarily controls personal memory.

### Project Memory

Examples:

- Decisions made in a project thread
- Prior discussions and agreed constraints
- Open questions carried forward

### Operational Memory

Examples:

- Previous incidents
- Lessons learned
- “What we tried last time” (continuity, not Standards/ADR authority)

### Temporary Context

Examples:

- Current conversation working set
- Short-lived reasoning scratch state
- In-flight agent task context mirrors (not agent-owned permanent memory)

Temporary Context expires aggressively and should not be treated as durable preference.

---

## Memory Lifecycle

```text
Capture
  ↓
Evaluate
  ↓
Classify
  ↓
Store
  ↓
Retrieve
  ↓
Use
  ↓
Review
  ↓
Expire / Update / Forget
```

| Stage | Purpose |
| --- | --- |
| **Capture** | Notice candidate continuity signals from conversation, decisions, outcomes, agent returns |
| **Evaluate** | Decide whether the signal should become memory at all |
| **Classify** | Assign category (User / Project / Operational / Temporary) |
| **Store** | Persist under governance (conceptual); no tech chosen |
| **Retrieve** | Select relevant memories for a request |
| **Use** | Enter Context Assembly with provenance |
| **Review** | User/KORA correction, confidence adjustment |
| **Expire / Update / Forget** | Time-bound removal, correction, or intentional deletion |

---

## Memory Governance

### What KORA may remember automatically

- Explicit user requests to remember
- Clearly stated durable preferences (as Memory, not Knowledge)
- Session-necessary Temporary Context
- Decision summaries the user accepted (Project/Operational Memory candidates)

### What requires confirmation

- Sensitive personal attributes
- Promotion from Temporary → durable categories when ambiguous
- Cross-project transfer of preferences
- Any candidate that could be mistaken for platform Knowledge

### What should never be stored

- Secrets, credentials, tokens, private keys
- Raw tool dumps with sensitive material unless redacted and explicitly approved
- Content the user forbids
- Unverified third-party personal data unrelated to the user’s request

### Memory confidence

Each durable memory should carry conceptual confidence:

- Explicitly stated by user (high)
- Inferred from pattern (low–medium; prefer confirmation)
- Contradicted / contested (surface conflict; do not silently win)

### User correction

- Users may correct Memory
- Corrections supersede prior conflicting Memory items
- Corrections do not rewrite Knowledge unless governance promotion occurs

### Memory deletion

- Users may delete personal Memory
- Project/Operational Memory deletion follows ownership/governance norms
- Deletion should be honored in future retrieval

### Memory expiration

- Temporary Context: short TTL / end-of-session default
- Inferred preferences: review/expire if unconfirmed
- Explicit preferences: durable until changed/deleted
- Operational lessons: retain until superseded by newer lesson or explicit forget

### Controlling principle

**The user controls personal memory.**

UX contract for view/correct/delete/approve flows: `User_Experience.md` and `Interaction_Model.md`.

---

## Retrieval Rules (Conceptual)

- Retrieve minimum sufficient Memory for the classified request
- Prefer explicit over inferred
- Prefer recent corrections over older statements
- Never present Memory as Knowledge authority
- Label provenance for Context Assembly
- Obey `Retrieval_Strategies.md`: preference/personal classes are Memory-only; architecture classes typically skip Memory
- Ranking/budgets: `Context_Ranking.md`

---

## Non-goals

- Vector DB / embedding / product selection
- Implementing a memory service
- Equating chat logs with governed Memory automatically

---

## Document Map

| Document | Role |
| --- | --- |
| `Memory_Runtime.md` (this file) | Runtime lifecycle and governance |
| `Memory.md` | Boundary definition |
| `Context_Intelligence.md` / `Retrieval_Strategies.md` | When Memory may be queried |
| `Context_Assembly.md` | How memory enters reasoning context |
| `Knowledge_Runtime.md` | Sibling runtime for reference corpus |
| `Documentation/Phase13/Memory_Runtime_Model.md` | Phase 13.5 report |
| `Documentation/Phase13/Context_Intelligence_Model.md` | Phase 13.12 report |
