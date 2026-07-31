# Phase 11 — Hermes Smoke Test

**Timestamp:** 2026-07-30T11:15:00Z  
**Result:** **FAIL** (core UI up; kanban permissions broken)

| Check | Result |
|-------|--------|
| Container | `running` |
| Data mount | `/mnt/monarch/appdata/hermes` → `/opt/data` |
| Traefik `https://hermes.fatherfankscloud.uk/` | 302 → `/login` |
| Logs | Recurring `PermissionError` on `/opt/data/kanban.db.init.lock` |

## Root cause (pre-existing)

- Gateway/dashboard processes run as **uid 10000**
- Appdata files owned by **uid 1000** (`fatherfrank`), lock file mode `0644`
- uid 10000 cannot write the lock → kanban dispatcher fails every tick

Inventory-only path — **no copy/restart** performed.
