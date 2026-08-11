# Memory Service Boundary Assessment

**Branch:** `phase14-hermes-runtime` (investigation only — no production change)
**Date:** 2026-08-11
**Question:** Can the existing Phase 14.2 Memory Runtime become a small KORA-owned HTTP service boundary for the Hermes-hosted KORA agent?

---

## Where each component actually lives (verified from code)

| Component | File | Lives in | Notes |
|---|---|---|---|
| Event Bus | `Runtime/app/event_bus.py` | in-process with the KORA Runtime | `InProcessEventBus` (sync, thread-safe); `EventBus` is a `Protocol`; `EventEnvelope` is JSON-serializable (`to_dict`/`from_dict`); publish validates JSON-serializability |
| Memory Runtime | `Runtime/app/memory_runtime.py` | in-process | `EventDrivenMemoryRuntime` subscribes to topics; `create_proposal()` is the eligibility/dedup/capacity/secret-check entry |
| Approval Engine | `Runtime/app/approval_engine.py` | in-process | `InMemoryApprovalEngine` — pure state transitions over the shared proposal dict |
| Pending proposals | `Runtime/app/proposal_repository.py` | in-process + SQLite | `InMemoryProposalRepository` / `SQLiteProposalRepository` (`proposals` + `proposal_audit`, redaction CHECK) |
| Durable memory | Honcho (external) | external service | reached only via `DurableMemoryStore` protocol |
| Honcho adapter | `Runtime/app/honcho_adapter.py` | in-process | `HonchoAdapter` HTTP client to `Honcho v3 /conclusions`; read ops exist (`list_memories`, `find_by_proposal_id`) but are **not** exposed over HTTP |
| Candidate entry | `main.py` + in-process bus | in-process | proposals are created ONLY by publishing `memory.candidate` (or `memory_candidate` payload) on the in-process bus → `_receive_event` → `create_proposal` |
| Approval/commit | `Runtime/app/commit_coordinator.py` | in-process | `MemoryCommitCoordinator.approve_and_commit` → approval engine → durable store → finalize |
| Composition | `main.py` (~15 lines) | in-process | `EVENT_BUS`, `PROPOSAL_REPOSITORY`, `MEMORY_RUNTIME`, `DURABLE_STORE`, `COMMIT_COORDINATOR`, `MEMORY_AUTHORIZER` |

## Existing HTTP API (all in `main.py`)

- `GET /v1/memory/proposals` · `GET /v1/memory/proposals/{id}`
- `POST /v1/memory/proposals/{id}/approve|reject|withdraw|expire`
- **Missing:** no `POST` to *submit/create* a proposal; **no committed-memory read endpoint** (Phase 14.2 deferred durable retrieval).

## Answers

1. **Can the existing Memory Runtime become a standalone KORA-owned service?** Yes. All nine memory modules are already decoupled from the FastAPI app (they do not import `main.py`), the `EventBus` is a `Protocol`, the repository and durable-store are pluggable. The composition in `main.py` (~15 lines) can be lifted into a small standalone FastAPI service with no changes to the memory internals.

2. **What code would need to move?** Only the *composition + routes* currently in `main.py`: the ~15-line wiring (event bus, repository, runtime, durable store, coordinator, authorizer) and the memory routes + startup recovery. New: a small service entry module.

3. **What can remain unchanged?** All of `event_bus.py`, `memory_runtime.py`, `memory_models.py`, `approval_engine.py`, `proposal_repository.py`, `commit_coordinator.py`, `durable_memory.py`, `honcho_adapter.py`, `auth.py`; the SQLite schema; the Honcho adapter; the approval→commit workflow.

4. **Minimum HTTP API.** The lifecycle routes already exist and move as-is; the two genuinely missing operations are:
   - `POST /memory/proposals` — **submit a memory candidate** (the missing link for the agent). Handler constructs an `EventEnvelope` and calls the existing `create_proposal()` → eligibility/confidence/category/secret checks, dedup, capacity, expiry → `pending_review`. **This is the only way candidates enter; approval is not bypassable.**
   - `GET /memory` (or `/memory/memories`) — **retrieve committed durable memory**, needed for the agent to "retrieve required memory state"; Phase 14.2 deferred this, but the read ops already exist on `HonchoAdapter.list_memories/find_by_proposal_id` and can be exposed as-is.

5. **How does the Event Bus work across the service boundary?** It does not need to cross the boundary. The service keeps the `InProcessEventBus` internal; the HTTP `POST /memory/proposals` handler builds an `EventEnvelope` and calls `create_proposal` (or publishes on the in-process bus). External agents use HTTP; the bus abstraction (Protocol + serializable envelope) is preserved for a future distributed transport if ever needed.

6. **How does the Approval Engine remain authoritative?** Every mutation goes through the existing `InMemoryApprovalEngine` transitions and `MemoryCommitCoordinator`. The HTTP routes are thin wrappers. `POST /memory/proposals` yields only `pending_review`; durable write to Honcho happens only via `approve_and_commit`.

7. **How does Honcho remain behind the Memory boundary?** Only the `MemoryCommitCoordinator` calls the `DurableMemoryStore` (Honcho). The service exposes no direct Honcho write route. Committed-memory reads would go through the same `DurableMemoryStore` protocol (KORA-owned).

8. **What persistence moves with the service?** The `SQLiteProposalRepository` (proposal state + audit trail with terminal-content redaction) — the same schema, pointed at a service-owned DB path (e.g. the existing `/data/memory-runtime.sqlite3`). Committed memory remains in Honcho (external). Startup `recover()` stays in the service.

9. **What authentication is required?** Extend the existing `BearerAuthorizer` scope model (`memory:read` / `memory:approve` / `memory:operate`) with a `memory:propose` (submit) scope for the agent token; keep read/approve/operate scopes for approval UIs/operators. Scoped tokens via env (currently unset in production — must be configured).

10. **Risks.** (a) DB ownership — during transition only one process may own the proposal SQLite file (the old runtime and the new service must not both write it); (b) committed-memory retrieval is net-new (currently deferred); (c) Honcho availability affects commit/read; (d) the in-process bus is lost for any *external* event producers (none exist today — bus consumers are internal); (e) no semantic/retrieval search on committed memory exists (out of scope for this boundary).

11. **How much code would actually need to change?** Minimal, and confined to a new service surface: a small FastAPI app (~100–200 lines) reusing the existing modules unchanged, plus two new routes (submit candidate, committed-memory read), plus one auth scope. Zero changes to the nine memory modules.

12. **Does this preserve the Phase 14.2 architecture?** Yes — same components, same approval-gated workflow, same persistence/redaction, same Honcho boundary. It only adds an HTTP surface in front of the existing `create_proposal`/`approve_and_commit` flow.

13. **Does this require a rewrite?** No.

14. **Does this require significant custom Python?** No — a small service module is legitimate KORA-owned infrastructure (composition + routes), not a proxy/bridge/replacement memory system.

15. **Is this worth doing before Hermes production migration?** Yes. It is the smallest change that unblocks the Hermes-hosted KORA agent's memory path (`KORA Agent → KORA Memory Service → Memory Runtime → Approval Engine → Honcho`) while preserving governance, and it is independent of the (separately blocked) pre-inference governance issue.

## Governance note (unchanged)

The Hermes pre-inference refusal limitation remains an independent migration blocker, documented and not addressed here. Graphify is verified reachable (MCP HTTP) and unchanged.

---

## Final verdict

**B — MODERATE REFACTOR**

On the A/B boundary and closer to A: the Phase 14.2 memory **internals extract cleanly with zero changes** (no rewrite, no new memory system, no significant custom Python). It is called a moderate refactor rather than a clean extraction because the service boundary requires meaningful, non-trivial work: (1) extracting the memory surface out of `main.py` into a standalone FastAPI service, (2) adding the missing **submit-candidate** operation, (3) adding a **committed-memory read path** that Phase 14.2 deferred, (4) adding a `memory:propose` auth scope, and (5) deciding SQLite DB ownership during transition.

Doing so is low-risk and worth it before the Hermes cutover. **No implementation was performed; production is untouched.**
