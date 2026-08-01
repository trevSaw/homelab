# KORA Runtime State Model

**Status:** Canonical runtime-state specification (Phase 13.14)  
**Platform:** KORA / Brainiac (`KORA.md`)  
**Rule:** State ownership follows architecture. Profiles may relocate *processes*; they may not relocate *authority*.

Companions: `Runtime_Contracts.md`, `Runtime_Observability.md`, `Runtime_Profiles.md`, `Vertical_Slice.md`

---

## Purpose

Define the lifecycle of a request and who owns each state so Solo, Simulated, Distributed, and Hybrid profiles share one state machine.

---

## Lifecycle

```text
User Request
    ↓
Classification
    ↓
Retrieval Strategy
    ↓
Retrieval
    ↓
Ranking
    ↓
Context Assembly
    ↓
Council
    ↓
Response
    ↓
Memory Candidate
    ↓
Knowledge Candidate
    ↓
Audit
```

Notes:

- Memory/Knowledge candidate stages occur only when the turn produces candidates; they are not mandatory every request.
- Expansion loops may re-enter Retrieval Strategy → Retrieval after Council gap detection.
- Forbidden actions may short-circuit to Response (refusal) + Audit with minimal retrieval.

---

## State Ownership

| State | Owner | Contents (conceptual) | Must not |
| --- | --- | --- | --- |
| **User Request** | UI layer (capture) → KORA | Message, session id, mode flags | Become Knowledge |
| **Classification** | KORA | Class label, ambiguity | Trigger retrieval early |
| **Retrieval Strategy** | Context Intelligence (KORA) | Allow/deny stores, budgets, priority | Query stores yet |
| **Retrieval** | Memory / Knowledge / Tools runtimes as allowed | Candidate evidence | Cross-store laundering |
| **Ranking** | Context Intelligence (KORA) | Scored/pruned set | Drop conflict counterparts silently |
| **Context Assembly** | KORA | Provenance-labeled package | Reopen skipped stores silently |
| **Council** | Council (Dynamics) under KORA facilitation | Contributions; selection record | Agents as seats; final user identity |
| **Response** | KORA synthesis → UI | Recommendation + explainability | Vendor brand as self |
| **Memory Candidate** | Memory Runtime + user governance | Pending approval artifact | Auto-commit |
| **Knowledge Candidate** | Knowledge Runtime + human/governance | Draft/candidate only | Silent Authoritative promotion |
| **Audit** | KORA / observability | Trace closeout; violations | Raw CoT; secrets |

---

## Durability Classes

| Class | Examples | Default durability |
| --- | --- | --- |
| **Ephemeral** | Temporary Context, ranking scratch, in-flight agent mirrors | Session / short TTL |
| **Candidate** | Memory pending approval; Knowledge drafts | Durable only as candidate, gated |
| **Governed durable** | Approved Memory; Authoritative Knowledge in repo/ADR process | Follow Memory/Knowledge governance |
| **Audit** | Classification/retrieval/refusal records | Per observability retention policy |

---

## Profile Independence

| Profile | State machine change? |
| --- | --- |
| Solo | **None** — Council state may be conceptual contributions |
| Simulated | **None** — contributions from structured prompts |
| Distributed | **None** — contributions may arrive from member runtimes |
| Hybrid | **None** — remote backends still owned by the same stages |

Moving Council deliberation to Hermes workers changes **where computation runs**, not **who owns Response identity** (KORA) or **who owns Knowledge SoT** (repo/ADRs).

---

## Transition Guards

| From → To | Guard |
| --- | --- |
| Request → Classification | Valid user message envelope |
| Classification → Strategy | Classification present |
| Strategy → Retrieval | Strategy selected; only allowed stores |
| Retrieval → Ranking | Candidates labeled |
| Ranking → Assembly | Budgets applied |
| Assembly → Council | Package provenance-complete |
| Council → Response | Synthesis by KORA |
| Response → Memory Candidate | Explicit preference/continuity signal; not automatic |
| Response → Knowledge Candidate | Explicit draft/promotion path; rare in default UX |
| Any → Audit | Always on completion/failure |

---

## Failure States

- **Missing evidence:** continue with gap flags; do not fabricate  
- **Refusal:** Response + Audit; Tools not executed  
- **Contract violation:** fail the turn; record Audit violation  

---

## Non-goals

- Database schemas
- Queue/broker selection
- Session store vendor choice

---

## Document Map

| Document | Role |
| --- | --- |
| `Runtime_State.md` (this file) | Lifecycle + ownership |
| `Runtime_Contracts.md` | Guarantees at each stage |
| `Runtime_Observability.md` | What to record at each stage |
| `Runtime_Profiles.md` | Hardware realizations of the same machine |
| `Vertical_Slice.md` | End-to-end architectural flow |
