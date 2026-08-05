# Memory Approval UX — Design Proposal (Phase 14.2 Preflight)

**Status:** Design contract only — **not implemented**  
**Authority:** `Architecture/ai/Memory.md`, `Memory_Runtime.md`, `User_Experience.md`, ADR-0005  
**Rule:** User is the final authority. No autonomous durable Memory writes.

This document defines the workflow Honcho (or any Memory backend) must obey before Phase 14.2 enables durable writes.

---

## Goals

1. Capture candidate memories without silently persisting them  
2. Let the user review, approve, edit, or reject  
3. Keep an auditable record of proposals and decisions  
4. Preserve Memory ≠ Knowledge (approval here never promotes Knowledge)

---

## Non-goals (this design)

- Implementing Honcho write APIs  
- Open WebUI built-in memory as KORA Memory  
- Automatic preference learning without review  
- Knowledge corpus ingestion (Phase 14.3)

---

## Actors

| Actor | Authority |
| --- | --- |
| **User** | Approve / reject / edit / delete personal Memory |
| **KORA** | Proposes candidates; never self-approves durable writes |
| **Memory Runtime (Honcho candidate)** | Stores candidates + durable items only after approval |
| **Open WebUI** | May display approval cards; does not own SoT |
| **Operator** | May audit; cannot silently approve personal Memory for the user |

---

## Proposal lifecycle

```text
capture_signal
    → draft_candidate          (ephemeral / staging)
    → pending_review           (visible to user)
    → { approved | rejected | expired | withdrawn }
    → if approved: durable_memory_item
    → optional: later correction / deletion
```

### States

| State | Meaning | Durable? |
| --- | --- | --- |
| `draft` | KORA assembled a candidate; not yet shown | No |
| `pending_review` | Awaiting explicit user decision | No |
| `approved` | User accepted (possibly after edit) | Yes (after commit) |
| `rejected` | User declined | No |
| `expired` | Timed out without decision | No |
| `withdrawn` | KORA/system withdrew (error, duplicate, unsafe) | No |
| `corrected` | Prior durable item superseded by user edit | Prior retained per retention policy |
| `deleted` | User forgot/removed durable item | Tombstoned / removed per policy |

**Transition rule:** `pending_review → approved` requires an **explicit** user action. Silence is not approval.

---

## What may be proposed

Examples aligned with Memory categories:

- Explicit user preference statements  
- Project decisions the user asked to remember  
- Operational lessons clearly marked as continuity (not Standards)

### Must not be proposed for auto-approval

- Secrets, credentials, tokens  
- Speculative inferences presented as facts  
- Live tool observations without user framing  
- Anything that would launder Memory into Knowledge

---

## Approval UX (conceptual)

### Surfaces (future)

1. **Inline chat card** (Open WebUI via KORA response metadata / plugin later)  
2. **Memory review panel** (“Pending memories”)  
3. **API** for headless/operator tooling (same state machine)

### Card contents (minimum)

- Proposed text (editable before approve)  
- Category: User / Project / Operational  
- Why proposed (short, no raw CoT)  
- Confidence / provenance (`source_class=conversation|user`, refs)  
- Actions: **Approve** · **Approve with edits** · **Reject** · **Defer**

### Copy principles

- Speak as **KORA**, not Honcho/Open WebUI  
- Ask permission; never announce “I saved that” unless approved  
- Rejection is normal and frictionless

---

## Rejection handling

| Case | Behavior |
| --- | --- |
| Reject | Mark `rejected`; do not persist durable content; keep audit stub |
| Defer | Remain `pending_review` until expiry |
| Expire | Move to `expired`; optional gentle re-prompt only if user re-triggers topic |
| Duplicate | Withdraw new candidate; point at existing durable item |

Rejected text must not be “soft-kept” in a hidden durable store.

---

## Metadata captured (per candidate)

| Field | Purpose |
| --- | --- |
| `candidate_id` | Stable ID |
| `created_at` / `decided_at` | Timeline |
| `proposed_by` | Always `kora` |
| `category` | user / project / operational |
| `text` / `text_final` | Proposed vs approved wording |
| `provenance` | Evidence refs (conversation turn ids, etc.) |
| `rationale_short` | Explainability-safe reason |
| `decision` | approved / rejected / expired / withdrawn |
| `decided_by` | user id / session |
| `backend` | e.g. `honcho` (implementation detail) |
| `schema_version` | Contract version |

---

## Audit trail expectations

1. Every state transition append-only (or equivalent immutable event log)  
2. Approvals record **final text** if edited  
3. Rejections record reason code optional; free-text optional  
4. Audit logs are **not** Knowledge and are not retrieved as Memory evidence by default  
5. Retention: configurable; personal audit visibility for the owning user  
6. Operators may access audits under homelab governance, not to silently rewrite personal Memory

---

## API considerations (future)

Conceptual endpoints (names illustrative):

| Operation | Semantics |
| --- | --- |
| `POST /memory/candidates` | KORA creates `pending_review` |
| `GET /memory/candidates?status=pending_review` | User review queue |
| `POST /memory/candidates/{id}/approve` | Body may include `text_final` |
| `POST /memory/candidates/{id}/reject` | Explicit rejection |
| `DELETE /memory/items/{id}` | User forget |

Guarantees:

- Backend adapters (Honcho) called **only** on approve/delete paths for durable store  
- Create-candidate must not call durable write APIs  
- Idempotent approve (double-submit safe)

---

## Separation from Open WebUI internal data

| Store | Role |
| --- | --- |
| Open WebUI `webui.db` / `vector_db` | UI application data only |
| KORA Memory Runtime | Durable continuity after approval |
| Staging candidates | KORA-controlled staging (not UI RAG) |

Open WebUI must not write candidates directly into Honcho. All proposals flow through KORA.

---

## Acceptance criteria for a future implementation PR

1. No durable Honcho write without `approved` transition  
2. UI/API requires explicit approve/reject  
3. Audit events exist for propose + decide  
4. Open WebUI RAG paths remain non-SoT  
5. Memory items never labeled as Knowledge  
6. Phase 13 Memory contracts unchanged

---

## Explicitly deferred to implementation (Phase 14.2+)

- Concrete Honcho API mapping  
- Open WebUI extension/plugin for cards  
- Retention job for `expired` candidates  
- Multi-user ACL details beyond single-homelab operator
