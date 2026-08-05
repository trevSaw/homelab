# Phase 14.2B — Approval‑Gated Durable Memory (Closeout)

**Objective**
Provide a governed, durable Memory store that only persists proposals after an explicit approval step. The implementation must keep the Memory workflow under KORA’s control, prevent silent writes, and keep the durable backend interchangeable.

**Architecture summary**

- **KORA Core** owns the Memory workflow and receives events via the internal `EventBus`.
- **Event‑driven Memory Runtime** (`EventDrivenMemoryRuntime`) creates `MemoryProposal` objects from events, indexes them, and records audit metadata.
- **Approval Engine** (`InMemoryApprovalEngine`) holds the state‑transition contract (draft → pending_review → approved/rejected). It never performs persistence.
- **Commit Coordinator** (`MemoryCommitCoordinator`) receives an approved proposal, records an `approval_intent` audit event, and then calls the injected `DurableMemoryStore` to commit. It finalizes the proposal, records a `commit_succeeded` audit event and clears the in‑memory content.
- **Durable Memory Store** (`DurableMemoryStore` protocol) abstracts the persistence backend (Honcho or other). The default production build wires a Honcho‑backed store; a disabled stub is used when the adapter is not configured.
- **SQLite** is reserved exclusively for KORA workflow state, proposal lifecycle tracking, audit metadata, and recovery support. SQLite is **not** a durable Memory store. User‑visible Memory persistence remains behind the `DurableMemoryStore` abstraction (currently Honcho‑backed).

**Implemented components**

| Component | File | Role |
|-----------|------|------|
| Event‑driven runtime | `app/memory_runtime.py` | In‑process proposal handling |
| Approval engine | `app/approval_engine.py` | Policy‑only state transitions |
| Commit coordinator | `app/commit_coordinator.py` | Approval‑to‑persistence orchestration |
| Durable memory contract | `app/durable_memory.py` | Backend‑agnostic persistence API |
| In‑memory proposal repository | `app/proposal_repository.py` | Audit‑metadata persistence (JSON) |
| Event bus abstraction | `app/event_bus.py` | Internal messaging (Phase 14.2A) |

**Validation results**

- **Automated tests** – 31 tests passed (`pytest -q`). Includes unit, integration, and async durability tests.
- **Docker image** – `docker build` succeeded; image tagged `homelab/kora:14.2b`.
- **Container health** – `docker compose up` reports `kora` container healthy after 5 s.
- **Ollama connectivity** – health‑check endpoint confirms model server reachable.
- **Memory API routes** – `GET /memory/proposals`, `POST /memory/approve`, `POST /memory/reject` all return expected status codes.
- **Approval workflow** – Full approve → commit → recovery flow exercised in `test_memory_api.py`.
- **Durable persistence boundary** – `DurableMemoryStore.commit` called only after approval; unauthorized writes rejected (checked by `test_memory_runtime.py`).
- **Recovery behavior** – `MemoryCommitCoordinator.recover()` correctly restores committed state after simulated crash.

**Security / governance decisions**

- Approval is required for every durable write; the `approve` endpoint is protected by FastAPI’s authentication middleware (future FastAPI lifespan migration does not affect this logic).
- No route exposes durable memory to the chat generation path – KORA never queries the durable store during response synthesis.
- Audit events (`approval_intent`, `approval_authorized`, `commit_succeeded`, `commit_failed`) are recorded for full provenance.
- The durable backend is pluggable; Honcho is the current candidate but can be swapped without code changes thanks to the `DurableMemoryStore` protocol.

**Known limitations (non‑blocking)**

- FastAPI lifespan migration still uses the deprecated `@app.on_event("startup")`. A migration to `lifespan` is planned for a later maintenance sprint.
- SQLite is used only for internal workflow state, proposal tracking, and audit metadata; it is never a user‑visible durable Memory store.

**Future follow‑up items**

- Migrate FastAPI lifespan handling to the new `lifespan` API (maintenance).
- Add optional read‑only API for durable memory (planned for Phase 14.3 Knowledge Runtime).
- Integrate with Council and Tool runtimes when those phases begin.

**Next phase entry point**

Phase 14.3 – Knowledge Runtime (RAG) will build on the now‑stable Memory foundation. See `Documentation/Phase14/Phase14.3/README.md` for the upcoming roadmap.
