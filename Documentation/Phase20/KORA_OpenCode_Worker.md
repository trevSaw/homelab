> **DEPRECATED (Phase 22).** Superseded by `Documentation/Phase22/KORA_OpenCode_Go_Migration.md` and ADR-0011. Hermes is now the agent harness; heavy coding uses Hermes delegation to an OpenCode Go-backed child (DeepSeek Flash). Task Bridge is targeted for removal after Go-path validation. This document is retained as historical reference.

# KORA ↔ OpenCode Remote Execution Integration (Phase 20)

**Status:** Implemented & validated 2026-09-23.
**Components:** `services/taskbridge` (Task Bridge) + Hermes MCP integration +
KORA plugin delegation directive.

This document describes how KORA delegates real server-side engineering and
troubleshooting tasks to **OpenCode running as a worker on mocha**, and how the
result flows back to KORA / Open WebUI / Discord.

## 1. Architecture

```text
Open WebUI ─────────────────────────────► Hermes api_server (:8642)
                                             │  KORA head agent (plugin)
                                             │  MCP tools: mcp_taskbridge_*
                                             ▼
                                     Task Bridge (container, :8643)
                                   REST API  +  Streamable HTTP MCP (/mcp)
                                             │  executes detached `opencode run`
                                             ▼
                                OpenCode worker (uid 1000)
                                cwd = /workspace = canonical homelab repo
                                   ├── inspect repo / git
                                   ├── inspect Docker state snapshots (ro)
                                   ├── web research
                                   ├── edit / validate (worktree or repo)
                                   └── report (structured)
                                             │  result + logs + validation
                                             ▼
                                     Task Bridge SQLite store
                                             │  mcp_taskbridge_get_task
                                             ▼
                                   KORA reports to Open WebUI
                                   (optional) Discord / ntfy webhook
```

**Components**

| Component | Where | Role |
| --- | --- | --- |
| Hermes v0.17.0 | container `hermes` | KORA runtime; exposes MCP tools to api_server sessions |
| KORA | Hermes plugin (`/opt/data/plugins/kora`) | Orchestrator; decides to delegate; interprets/reports results |
| Task Bridge | container `taskbridge` (`homelab/taskbridge:1.0.0`) | Task/execution interface: queue, persistence, approval, OpenCode subprocess, validation, notifications |
| OpenCode 1.18.32 | in bridge image (`/usr/local/bin/opencode`) | Execution agent (workers `kora-readonly`/`kora-testwrite`/`kora-write`) |
| Ollama | container `ollama` | Worker model `gpt-oss:20b-cloud` (same model KORA uses) |
| Open WebUI | container `open-webui` | Unchanged; routes to Hermes `:8642` as before |

## 2. API / interface used

### Hermes → Task Bridge (MCP, Streamable HTTP)

`/mnt/monarch/appdata/hermes/config.yaml`:

```yaml
mcp_servers:
  taskbridge:
    url: http://taskbridge:8643/mcp
    headers:
      Authorization: "Bearer <TASKBRIDGE_API_TOKEN>"
    tools:
      include: [create_task, get_task, list_tasks, cancel_task, approve_task]
platform_toolsets:
  api_server:
    - kora
    - file
    - terminal
    - taskbridge   # explicit MCP allowlist for the api_server platform
```

Exposed tool names to KORA: `mcp_taskbridge_create_task`,
`mcp_taskbridge_get_task`, `mcp_taskbridge_list_tasks`,
`mcp_taskbridge_cancel_task`, `mcp_taskbridge_approve_task`.

### Task Bridge REST API

All endpoints require `Authorization: Bearer <TASKBRIDGE_API_TOKEN>`:

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/api/v1/tasks` | Create task (`request`, `permission_profile`, `requested_by`, `session_id`, `timeout_seconds`) |
| `GET` | `/api/v1/tasks/{id}` | Status + result |
| `GET` | `/api/v1/tasks` | List (`limit`, `status`) |
| `POST` | `/api/v1/tasks/{id}/approve` | Approve a `production_write` task |
| `POST` | `/api/v1/tasks/{id}/cancel` | Cancel a queued/running task |
| `GET` | `/api/v1/health` | Health |

### Task model (SQLite)

```
KORA-YYYYMMDD-NNNN
  request, permission_profile, working_directory,
  requested_by, approved_by, session_id, timeout_seconds,
  status, opencode_session, process_pid,
  created_at / started_at / completed_at, exit_code,
  result (summary, investigation, changes, validation,
          production_impact, follow_up, raw_text, validation_checks),
  error
```

## 3. Authentication

- Hermes→Bridge: bearer token in MCP `headers` (config.yaml), plus the explicit
  `taskbridge` toolset allowlist. Gateway restart required after config edit.
- REST: bearer token on every request (FastAPI dependency + MCP middleware).
- The token lives in `services/taskbridge/.env` (gitignored) and in the Hermes
  config.yaml (on the hermes volume, `0600`). No secrets in git.
- Open WebUI auth unchanged (Hermes `API_SERVER_KEY`).

## 4. Task lifecycle & states

```
QUEUED ──► STARTING ──► RUNNING ──► VALIDATING ──► COMPLETED
  │                         │            │
  │  (production_write)     │            └──► FAILED (validation failed)
  ▼                         └──► FAILED / CANCELLED
WAITING_FOR_APPROVAL ──approve──► QUEUED
```

- `FAILED` — OpenCode non-zero exit, launch error, timeout, interrupted by
  bridge restart, or validation failure.
- `CANCELLED` — via `cancel_task` / REST cancel (kills the process group).
- State is persistent; a disconnected client can reconnect and retrieve it.

## 5. Permissions & execution boundaries

| Profile | Agent | Enforced by | Production impact |
| --- | --- | --- | --- |
| `read_only` | `kora-readonly` | OpenCode `permission`: edit/write/patch **deny**; mutating bash **deny** | None |
| `test_write` | `kora-testwrite` | edits allowed **only in an isolated git worktree**; production commands deny | None |
| `production_write` | `kora-write` | canonical repo + Compose apply allowed; **approval-gated** (`WAITING_FOR_APPROVAL`) | Yes |

Denial is mechanical (OpenCode permission engine), not prompt-based. The
permission rules live in `services/taskbridge/opencode/opencode.jsonc`.

## 6. Governance boundaries

- **Repository-as-source-of-truth.** The worker operates on the canonical
  homelab repo (or a detached worktree). It is instructed to consult
  `/workspace/Architecture/standards/` (DockerStandard, Service Lifecycle,
  ADRStandard, BackupStandard, SecurityStandard) before changes.
- **No `.env` exposure.** Workers are permission-blocked and instructed never
  to read `.env`; fresh worktrees contain no untracked secrets.
- **Validation is mandatory.** Changed compose files are validated with
  `docker-compose config -q`; `git diff --check` and `git status --porcelain`
  are captured into the result. Success is never claimed from exit code alone.
- **Backups before mutation.** `production_write` records git HEAD + status +
  diff before running, and reports what was backed up.
- **No `docker.sock`.** Docker state comes from host-generated read-only
  snapshots (Phase 18.1 pattern). Live container mutation is not exposed to
  any container.

## 7. Discord integration

- **Notifications (implemented):** set `TASKBRIDGE_DISCORD_WEBHOOK` in
  `services/taskbridge/.env`; the bridge posts task start/approval-required/
  completion/failure notifications to that webhook. Outbound only; OpenCode is
  never exposed to Discord.
- **Input channel + richer output (requires a Discord bot token):** Hermes
  natively supports a Discord platform. Configure it (`hermes gateway setup` +
  bot token, or add the token to Hermes env), then users can message KORA
  directly on Discord; KORA delegates through the bridge and answers back in
  the same channel (`hermes send` / native gateway). The token is an external
  dependency the owner must supply; until then the webhook path is used.

## 8. Open WebUI integration

Unchanged: Open WebUI → `http://hermes:8642/v1` (model `KORA`). Users simply
ask KORA, e.g. *"Investigate why Sonarr is failing to import downloads. Don't
make changes."* KORA delegates, replies *"Task KORA-… started."*, and on
follow-up (*"what was the result of task …?"*) retrieves and reports the
result. No UI changes required.

## 9. Failure handling

- OpenCode crash / non-zero exit → `FAILED`, logs preserved.
- Timeout → `FAILED (timeout)`, process killed.
- Bridge restart while a task runs → task swept to `FAILED (interrupted)` with
  state preserved (no automatic resume).
- Web research failure → reflected in the report; task can still complete if
  the core work succeeded.
- Partial results → preserved in `raw_text` + `log`; `no_text_output` flag set
  if OpenCode exits 0 without producing a report.
- Cancellation → process group killed, `CANCELLED`.

## 10. Observability

- `docker exec taskbridge python3 -c "... /api/v1/tasks?status=running"` —
  what is running.
- `GET /api/v1/tasks/{id}` — requester, permissions, files changed
  (`validation_checks.git_status_porcelain`), whether production was touched
  (`production_impact`), validation result, failure reason.
- Per-task raw log: `/mnt/monarch/appdata/taskbridge/logs/<task_id>.log`.
- OpenCode session id is stored for each task (auditable via
  `opencode export <session>`).

## 11. How to inspect / cancel / approve

```sh
# inspect
curl -H "Authorization: Bearer $TOKEN" http://taskbridge:8643/api/v1/tasks?status=running   # from a proxy-net host
# cancel
curl -X POST -H "Authorization: Bearer $TOKEN" http://taskbridge:8643/api/v1/tasks/<id>/cancel
# approve a production_write task (only after owner consent)
curl -X POST -d '{"approver":"homelab-owner"}' -H "Authorization: Bearer $TOKEN" http://taskbridge:8643/api/v1/tasks/<id>/approve
```

From Open WebUI, simply ask KORA to cancel/approve — it uses the same MCP tools.

## 12. Recovery procedure

- **Bridge down:** `docker compose up -d --build` in `services/taskbridge`.
  Interrupted tasks are failed (not lost); re-run them via KORA if needed.
- **Hermes config regression:** restore
  `/opt/data/config.yaml.bak-taskbridge-*` on the hermes volume and restart
  Hermes.
- **KORA plugin regression:** restore
  `/opt/data/plugins/kora/__init__.py.bak-taskbridge-*` and restart Hermes.
- **Full rollback:** see ADR-0010 / rollback below.

## 13. Known limitations

- Worker investigation depth depends on the model (`gpt-oss:20b-cloud`);
  open-ended tasks can be shallow. Use `TASKBRIDGE_MODEL` for a stronger model.
- KORA's delegation decision is probabilistic; the plugin directive strongly
  biases toward delegation but a small model may still answer directly.
- No automatic resume of interrupted tasks.
- Live Docker *mutations* (start/stop/restart, `compose up`) by the worker are
  not yet wired to a Docker socket (security stance); production apply is
  therefore limited to repo/Compose-file changes + validation. A scoped,
  approval-gated docker control surface is a follow-up.
- Discord input requires a bot token (external dependency).

## 14. Rollback

1. `docker compose -f services/taskbridge/compose.yaml down` (remove container).
2. Remove `mcp_servers.taskbridge` and `taskbridge` from
   `platform_toolsets.api_server` in `/mnt/monarch/appdata/hermes/config.yaml`
   (or restore the `config.yaml.bak-taskbridge-*` backup); restart Hermes.
3. Restore the pre-integration KORA plugin (`__init__.py.bak-taskbridge-*`),
   restart Hermes.
4. Optionally delete `/mnt/monarch/appdata/taskbridge`.
No production service compose files were modified by the integration itself.

## 15. Phase 21 — minimization & hardening (2026-09-23)

Audit-driven cleanup that keeps the Phase 20 boundary intact:

- **Pinned binaries in-image.** OpenCode (1.18.32) and docker-compose (v5.1.4)
  are now downloaded at image build time from their official releases and
  verified by SHA-256 in the `Dockerfile` ARGs. The previous host-copy
  `scripts/sync-binaries.sh` and `bin/` directory were removed; builds are
  reproducible from a clean checkout with no host-binary dependency.
- **Dead config removed.** `API_SERVER_KEY` and `TASKBRIDGE_DOCKER_STATE` were
  unused (the worker calls Ollama directly); the stale `model` default was
  aligned to `ollama/gpt-oss:20b-cloud`.
- **Mechanical canonical-tree boundary check.** `read_only` and `test_write`
  tasks snapshot the canonical repo working tree (`git status --porcelain` +
  `git diff --stat`) before execution and re-check afterwards; any change fails
  the task with `boundary_violation` (recorded in `result.boundary_check`)
  even if OpenCode exited 0.
- **Validation order fixed.** `test_write` validation now runs while the
  worktree still exists (previously it ran after worktree cleanup and could not
  read the worktree). Worktree metadata is pruned after removal.
- **Cancellation preserved.** A task cancelled mid-run now stays `CANCELLED`
  (previously the failure path overwrote it to `FAILED`).
- **Orphan-process cleanup.** If a task launch raises after spawn, the worker
  process group is killed best-effort; helper commands now raise on non-zero
  exit so failures are surfaced rather than silently swallowed.
- **Native Hermes OpenCode skill** (installed upstream, v1.2.0) is intentionally
  **not** used for homelab execution: it runs inside the Hermes container (uid
  10000) which has no access to the canonical repository, and enabling repo
  access there would reintroduce the Phase 18.1 `.env` exposure. See the
  Phase 20.5 audit. The Task Bridge remains the governed execution boundary.