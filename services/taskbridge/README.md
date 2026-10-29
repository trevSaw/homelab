> **DEPRECATED (Phase 22) — pending removal.** Superseded by Hermes delegation to OpenCode Go (ADR-0011). Do not extend this service; it will be removed once the Go path is validated.

---
title: Task Bridge Service README
document_type: README
service: taskbridge
owner: Homelab
status: Active
version: 1.0.0
last_reviewed: 2026-09-23
related_documents:
  - Architecture/decisions/ADR-0010-KORA-Execution-Worker-OpenCode-Task-Bridge.md
  - Documentation/Phase20/KORA_OpenCode_Worker.md
  - Documentation/Phase18/KORA_Controlled_Development_and_Validation.md
---

# Task Bridge (KORA → OpenCode execution worker)

The **Task Bridge** is the execution interface between KORA (the Hermes-hosted
orchestration agent) and **OpenCode** running as a detached engineering worker.
KORA delegates a task via an MCP tool, the bridge executes `opencode run` as an
async subprocess against the canonical homelab repo, persists the lifecycle +
result, and KORA retrieves/reports the result.

## Components

- **REST API** (`:8643`, internal-only on the `proxy` network) — task CRUD,
  status, approve, cancel. Token-authenticated.
- **Streamable HTTP MCP endpoint** (`/mcp`) — the tools KORA sees:
  `create_task`, `get_task`, `list_tasks`, `cancel_task`, `approve_task`
  (registered to Hermes as `mcp_taskbridge_*`).
- **OpenCode worker agents** — `kora-readonly`, `kora-testwrite`, `kora-write`
  with mechanical permission profiles (see `opencode/opencode.jsonc`).
- **Task store** — SQLite at `/mnt/monarch/appdata/taskbridge/tasks.db`; logs at
  `.../logs/<task>.log`; worktrees at `.../worktrees/`.

## Execution boundaries

| Profile | Runs in | Can edit | Production | Requires approval |
| --- | --- | --- | --- | --- |
| `read_only` | canonical repo | No (edit/write/patch denied) | No | No |
| `test_write` | isolated git worktree | Yes (worktree only) | No | No |
| `production_write` | canonical repo | Yes | Yes | **Yes** (`WAITING_FOR_APPROVAL`) |

As defense-in-depth, `read_only` and `test_write` tasks snapshot the canonical
repository working tree (`git status --porcelain` + `git diff --stat`) before
execution and re-check it afterwards; any change to the canonical tree fails the
task with `boundary_violation` even if OpenCode exited 0.

## Task lifecycle

`QUEUED → STARTING → RUNNING → VALIDATING → COMPLETED`
with `FAILED`, `CANCELLED`, `WAITING_FOR_APPROVAL` (and interrupted tasks on
bridge restart are failed with state preserved).

## Operate

```sh
cd services/taskbridge
docker compose up -d --build    # build & start (binaries pinned in-image, sha256-verified)
docker compose logs -f          # watch
```

The image downloads the pinned OpenCode and docker-compose release binaries at
build time (exact versions + SHA-256 in `Dockerfile` ARGs) — there is no host
binary to copy and no build-time host dependency.

API examples (run from inside the container or another proxy-network host):

```sh
T="<TASKBRIDGE_API_TOKEN>"
# create a read-only task
docker exec taskbridge python3 -c "import urllib.request,json; \
b=json.dumps({'request':'Inspect services/sonarr/compose.yml and report the image tag','permission_profile':'read_only','requested_by':'ops'}).encode(); \
r=urllib.request.Request('http://127.0.0.1:8643/api/v1/tasks',data=b,headers={'Content-Type':'application/json','Authorization':'Bearer $T'},method='POST'); \
print(json.load(urllib.request.urlopen(r)).get('id'))"
# get status/result
docker exec taskbridge python3 -c "import urllib.request,json; \
r=urllib.request.Request('http://127.0.0.1:8643/api/v1/tasks/<TASK_ID>',headers={'Authorization':'Bearer $T'}); \
print(json.dumps(json.load(urllib.request.urlopen(r)),indent=1))"
# approve a production_write task
docker exec taskbridge python3 -c "import urllib.request,json; \
b=json.dumps({'approver':'homelab-owner'}).encode(); \
r=urllib.request.Request('http://127.0.0.1:8643/api/v1/tasks/<TASK_ID>/approve',data=b,headers={'Content-Type':'application/json','Authorization':'Bearer $T'},method='POST'); \
print(json.load(urllib.request.urlopen(r)).get('status'))"
# cancel
docker exec taskbridge python3 -c "import urllib.request,json; \
r=urllib.request.Request('http://127.0.0.1:8643/api/v1/tasks/<TASK_ID>/cancel',data=b'{}',headers={'Content-Type':'application/json','Authorization':'Bearer $T'},method='POST'); \
print(json.load(urllib.request.urlopen(r)).get('status'))"
```

## Security

- No published host ports; service is reachable only on the `proxy`/`ollama-net`
  Docker networks. Token auth on every endpoint (MCP included).
- No `docker.sock`. Docker state comes from read-only host snapshots
  (`/home/fatherfrank/projects/docker-state`, `:ro`).
- Workers are uid 1000 (repo owner), read `.env` is denied by permission rules
  and worker rules; `.env` files are never mounted into the workspace copy
  (fresh worktrees contain no untracked secrets).
- `production_write` requires explicit approval; approver is recorded.
- Notifications are outbound-only (Discord webhook / ntfy) and optional.

## Model

The worker uses `gpt-oss:20b-cloud` directly via Ollama (same model KORA uses).
Override with `TASKBRIDGE_MODEL` in `.env` (e.g. `ollama/qwen3.5:397b-cloud`)
for stronger agentic behavior.