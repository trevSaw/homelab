# Phase 14.2D — Deployment Recommendations

## Canonical test command

```bash
PYTHONPATH=AI/KORA/Runtime:AI/KORA python3 -m pytest
```

This is the repository's canonical execution method. Do not add `conftest.py` or
sys.path bootstrapping inside tests.

## Deploying KORA

1. Ensure external networks exist: `ollama_ollama-net`, `proxy`.
2. Ensure Ollama is up and healthy first (KORA depends on it for chat).
3. Copy `services/kora/.env.example` to `services/kora/.env` and set:
   - `KORA_MEMORY_READ_TOKEN`, `KORA_MEMORY_APPROVAL_TOKEN`,
     `KORA_MEMORY_OPERATOR_TOKEN` (distinct high-entropy values)
   - `KORA_HONCHO_BASE_URL` (if Honcho enabled)
4. `docker compose -f services/kora/compose.yaml build`
5. `docker compose -f services/kora/compose.yaml up -d`
6. Verify: `docker inspect kora --format '{{.State.Health.Status}}'` → `healthy`

## Startup order

`ollama → kora → open-webui`. These are separate compose projects; do not use
`depends_on` across projects.

## Health

- `GET /health` on port 8080 returns `status: ok` when Ollama reachable,
  `degraded` otherwise.
- KORA container healthcheck uses the same endpoint (30s interval, 5 retries).

## Memory API

Authenticated Bearer-token endpoints under `/v1/memory/proposals` with scopes:
`memory:read`, `memory:approve`, `memory:operate`.

## Backups

`/data` (SQLite workflow state) is the persistence point for Memory workflow
state. Back up `/mnt/monarch/appdata/kora` and Honcho's Postgres volume. Durable
Memory itself lives in Honcho.

## Logging

- Set `KORA_LOG_LEVEL` (INFO default).
- Centralized logging label `com.homelab.logging=central` on the KORA service.
