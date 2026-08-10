# ADR‑14.2B‑001 – Approval‑Gated Durable Memory

**Status:** ✅ Accepted (Phase 14.2B complete)

## Context
Phase 14.2A introduced an event‑driven Memory runtime with an in‑memory proposal model and read‑only status APIs. Durable persistence was deliberately deferred to avoid ungated writes (ADR‑0005).

## Decision
1. **All durable Memory writes must be explicitly approved** via the `approve` endpoint before any persistence backend is invoked.
2. **The Approval Engine** (`InMemoryApprovalEngine`) is a pure state‑transition contract; it never performs I/O.
3. **Durable persistence is performed by a `DurableMemoryStore` implementation** (Honcho or future adapter). The store is injected into `MemoryCommitCoordinator`, keeping the backend interchangeable.
4. **KORA remains the sole orchestrator** of the approval‑to‑persistence workflow; no other service may bypass it.
5. **SQLite** is reserved exclusively for KORA workflow state, proposal lifecycle tracking, audit metadata, and recovery support. SQLite is **not** a durable Memory store.
6. **Memory retrieval is still disabled** – the APIs expose proposal status and approval workflow state only; durable Memory retrieval is deferred to a later phase.

## Consequences
* Guarantees that no silent writes can occur, meeting the governance requirement of “no un‑approved persistence”.
* Enables auditability: every durable write is linked to an `approval_intent` and `commit_succeeded` audit event.
* Allows future backends (e.g., a different database) to replace Honcho without changing the KORA core.
* Retrieval APIs can be added later (Phase 14.3 Knowledge Platform) without retrofitting the approval contract.
