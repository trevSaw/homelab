# Phase 11 — Honcho Smoke Test

**Timestamp:** 2026-07-30T11:01:30Z  
**Result:** **FAIL**

| Check | Result |
|-------|--------|
| Containers | All `running` |
| Postgres mount | `/mnt/monarch/appdata/honcho/postgres` |
| Redis mount | `/mnt/monarch/appdata/honcho/redis` (PONG OK) |
| `psql` inside DB | **FAIL** — `could not open file "global/pg_filenode.map": Permission denied` |
| Traefik `honcho.fatherfankscloud.uk` | timeout / unreachable |
| API logs | Last clean startup 2026-07-25; no recent request logs |

## Root cause (pre-existing; not introduced by this batch)

- `pgdata` owned by **uid/gid 1000** with mode `0600` on critical files.
- Postgres server process cannot open `global/pg_filenode.map` as the DB role.
- 491 permission-denied log lines; ongoing within the last hour.
- Framework path was inventory-only — **no copy/restart performed**.

## Decision

Do **not** auto-chown/fix Postgres data without an explicit operator maintenance window.
