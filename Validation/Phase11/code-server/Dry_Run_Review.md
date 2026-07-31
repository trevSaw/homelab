# Phase 11 — code-server Dry-Run Review

**Generated:** 2026-07-30T09:32:00Z  
**Status:** APPROVED — proceed to execute copy  
**Mode:** `--dry-run` only (no mutations)

## Review checklist

| Check | Result |
|-------|--------|
| Source path | `/hive/code-server/config` — matches live bind → `/config` |
| Destination path | `/mnt/monarch/appdata/code-server` — correct |
| Migration size | ~1.6GB (config/extensions/workspace; no media datasets) |
| Exclusions | None |
| Compose changes | Single volume rewrite `/hive/code-server/config` → `/mnt/monarch/appdata/code-server` |
| Unrelated mounts | Repo also enables RO `/hive` and `/mnt/monarch/appdata` workspace mounts (commented out on live) — intentional Phase 8.5 tooling; not a data migration |
| Expected downtime | Longer than Portainer/Homepage due to ~1.6GB rsync |
| Permissions | `fatherfrank:fatherfrank` on config |
| `.env` | Created gitignored `services/code-server/.env` with `PASSWORD` from live (not committed) |

## Proposed compose diff

```
-      - /hive/code-server/config:/config
+      - /mnt/monarch/appdata/code-server:/config
```

## Warnings (expected)

- Proposed-dir missing `.env` during compose config check — live `.env` remains beside compose for apply
- Git working tree not clean — EXPECTED

## Decision

**APPROVED** — execute copy without `--apply-compose`, then apply compose after verify + cutover sync.
