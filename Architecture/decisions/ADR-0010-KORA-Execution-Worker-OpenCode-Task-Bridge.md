---
title: ADR-0010 KORA Execution Worker — OpenCode Task Bridge
document_type: ADR
service: taskbridge
owner: Homelab
status: Superseded by ADR-0011 (Phase 22)
version: 1.0.0
last_reviewed: 2026-09-23
related_documents:
  - Architecture/decisions/ADR-0004-KORA-Orchestration-Hermes.md
  - Documentation/Phase18/KORA_Controlled_Development_and_Validation.md
  - Documentation/Phase20/KORA_OpenCode_Worker.md
  - Architecture/standards/DockerStandard.md
  - Architecture/standards/SecurityStandard.md
  - services/taskbridge/README.md
---

# ADR-0010 — KORA Execution Worker (OpenCode Task Bridge)

## Status

**Accepted (Phase 20)** — implemented and validated end-to-end 2026-09-23.

## Context

KORA (the homelab orchestration agent, hosted in Hermes) is the conversational
authority but has deliberately **no execution authority**: it runs as a
non-root container user without Docker access, without host filesystem access,
and with writes scoped to its own workspace (Phase 17/18). Engineering work —
inspecting the repository or Docker state, researching how to deploy something,
drafting and validating service changes, applying approved remediations — must
be performed by an **execution worker** that KORA orchestrates.

Requirements established for this decision:

1. Tasks must be **asynchronous** and survive browser/SSH/Open WebUI
   disconnects; results must be retrievable after reconnection.
2. KORA must remain the conversational/orchestration authority — the worker is
   a subordinate execution agent, not a second KORA.
3. Homelab governance (repository-as-source-of-truth, pinned images, `.env`
   secrecy, validation, backups) must remain authoritative.
4. Clear execution boundaries: `read_only` / `test_write` / `production_write`,
   with explicit approval semantics for production mutations.
5. Internal-only communication; OpenCode must not be exposed publicly or to
   Discord/the internet directly.

## Decision

Adopt a containerized **Task Bridge** (`services/taskbridge`, image
`homelab/taskbridge:1.0.0`) as the execution interface between KORA and
OpenCode, reusing Hermes' native **MCP (Streamable HTTP)** mechanism.

```
Open WebUI ──► Hermes (KORA agent, api_server :8642)
                  │  MCP tools: mcp_taskbridge_*
                  ▼
            Task Bridge (container, proxy network, token-auth)
                  │  executes detached `opencode run`
                  ▼
            OpenCode worker (uid 1000, /workspace = canonical repo)
                  │  result (structured report + logs + validation)
                  ▼
            Task Bridge (persistent SQLite task store)
                  │  retrieval: mcp_taskbridge_get_task / REST
                  ▼
            KORA reports to Open WebUI  (+ optional Discord/ntfy webhook)
```

Key properties:

- **Execution surface**: the canonical homelab repository is mounted read-write
  at `/workspace` and owned by uid 1000 (matching the container worker user),
  so file writes carry the correct owner. No `docker.sock` is exposed; Docker
  state is read from host-generated read-only snapshots
  (`/home/fatherfrank/projects/docker-state`), extending the Phase 18.1 pattern.
- **Worker model**: OpenCode runs against `gpt-oss:20b-cloud` **directly via
  Ollama** (`http://ollama:11434/v1`), the same model KORA uses. The worker
  bypasses the Hermes api_server conversational layer to avoid OpenAI
  message-format incompatibilities with OpenCode's agent tool-progress events.
- **Execution boundaries** are enforced mechanically by per-agent OpenCode
  permission profiles baked into the bridge image:
  - `kora-readonly` — `edit`/`write`/`patch` denied; mutating bash commands
    (git commit/push/checkout/reset, docker start/stop/restart/rm, `rm -rf`,
    etc.) denied.
  - `kora-testwrite` — edits allowed **only inside an isolated git worktree**
    created per task (canonical working tree untouched); production mutation
    commands denied.
  - `kora-write` — canonical-repo edits + Compose apply allowed; **only after
    explicit approval** (task enters `WAITING_FOR_APPROVAL`; it does not run
    until `approve_task`/REST approve is called and `approved_by` is recorded).
- **Task lifecycle**: `QUEUED → STARTING → RUNNING → VALIDATING → COMPLETED`
  with `FAILED`, `CANCELLED`, and `WAITING_FOR_APPROVAL` states. Tasks are
  persisted in SQLite under `/mnt/monarch/appdata/taskbridge/`; per-task logs
  are preserved. Tasks serialized per repository (one `RUNNING` at a time);
  a startup sweep fails any task left `RUNNING` across a bridge restart.
- **Result reporting**: structured report (Summary / Investigation / Changes /
  Validation / Production impact / Follow-up) plus raw text, OpenCode session
  id, git status, and Compose `config -q` validation where compose files
  changed. A task is only `COMPLETED` when OpenCode exits 0 **and** the report
  was produced; empty-output tasks are flagged, never silently reported as
  success.
- **Auth**: REST + MCP endpoints require `Authorization: Bearer
  <TASKBRIDGE_API_TOKEN>` (Hermes sends it via `mcp_servers.taskbridge.headers`).
- **Networking**: bridge is on the `proxy` (Hermes/Open WebUI reachable) and
  `ollama-net` (worker model) Docker networks. No host ports are published; the
  service is internal-only.

## Alternatives Considered

| Alternative | Pros | Cons | Verdict |
| --- | --- | --- | --- |
| Host-native bridge process | No container overhead | Hermes containers cannot reach the host (host-gateway firewalled off — verified by connectivity test) | Rejected |
| Expose Docker socket to a worker container | Live Docker control | Unrestricted socket proxy risk; violates Phase 18 security stance | Rejected (read-only snapshots instead) |
| Hermes kanban as the task store | Durable, native lifecycle | Workers are Hermes profiles, not OpenCode; host/container boundary awkward | Rejected for MVP; kanban remains available for agent-side work |
| OpenCode `serve` persistent server + API | Lower per-task startup cost | Shared state, more moving parts, restart handling | Deferred; per-task detached `opencode run` is simpler and crash-isolated |
| Let KORA use its `terminal` toolset + curl | No new component | Fragile (model-built curl/JSON), container-scoped, ungoverned | Rejected; MCP gives structured tool contracts |
| Point the worker at the Hermes api_server for inference | Single LLM entry | OpenCode tool-progress messages are rejected by the api_server message validator (verified) | Rejected; worker uses Ollama directly |

## Consequences

**Positive:**
- KORA gains governed, asynchronous execution authority without becoming an
  unrestricted shell.
- Execution boundaries are enforced by OpenCode's permission engine (deny is
  mechanical, not prompt-based), with approval-gated production writes.
- Result quality and honesty are improved: structured reports, preserved logs,
  validation checks, and explicit production-impact tracking.
- No new secrets in the repo; `.env` files remain gitignored; workers are
  instructed (and permission-scoped) never to read them.

**Negative / Risks:**
- Worker output quality depends on the configured model
  (`gpt-oss:20b-cloud` is a small local model; open-ended investigation can be
  shallow). Mitigate by setting `TASKBRIDGE_MODEL` to a stronger model or by
  giving KORA more explicit task scoping.
- In-flight tasks are lost if the bridge container restarts (marked FAILED with
  preserved state); there is no automatic resume. Documented limitation.
- KORA's decision to delegate is probabilistic (LLM behavior); the plugin
  directive biases strongly toward delegation for operational work, but a small
  model may still answer directly for some requests.
- Discord input requires a Discord bot token configured in Hermes (external
  dependency); outbound webhook notifications are already supported.

## Implementation Notes

- Deployment: `services/taskbridge/` (Dockerfile + compose + opencode worker
  config + bridge source). OpenCode (1.18.32) and docker-compose (v5.1.4) are
  pinned **inside the image** at build time via Dockerfile ARGs with SHA-256
  verification (reproducible from a clean checkout; no host binaries are copied).
- **Phase 21 (2026-09-23):** removed the host-binary sync script in favour of
  in-image pinned downloads; removed dead `API_SERVER_KEY`/`docker_state_dir`
  config (the worker talks to Ollama directly); added a mechanical canonical-repo
  boundary check for `read_only`/`test_write` tasks (a changed canonical working
  tree fails the task with `boundary_violation`); fixed an issue where a cancelled
  task was later overwritten to `FAILED`; added best-effort orphan-process cleanup
  on launch errors. The REST API is retained as the operational surface for
  host-side approve/cancel/status and the Compose healthcheck; MCP remains the
  KORA-facing interface.
- Hermes runtime config (`/mnt/monarch/appdata/hermes/config.yaml`) requires:
  - `mcp_servers.taskbridge` (Streamable HTTP `url`, `headers` bearer token,
    `tools.include` of the five task tools), and
  - `platform_toolsets.api_server` extended with the MCP server allowlist so
    the api_server platform exposes the tools.
  - Gateway restart to load.
- KORA delegation directive added to the `kora` plugin `pre_llm_call` hook
  (persisted at `/mnt/monarch/appdata/hermes/plugins/kora/__init__.py`).
- Rollback: stop `taskbridge`, remove the `mcp_servers.taskbridge` +
  `platform_toolsets.api_server` entries from Hermes config, restart Hermes,
  and revert the plugin directive (backups are written alongside each edit).
  No production compose files are modified by the bridge unless an approved
  `production_write` task does so.