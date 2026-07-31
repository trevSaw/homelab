# Phase 11 — Homepage Dry-Run Review

**Generated:** 2026-07-30T09:25:00Z  
**Status:** APPROVED — proceed to execute copies, then align env  
**Mode:** `--dry-run` only (no mutations)

## Scope

Homepage is a two-path migration (same stack):

| Key | Source | Destination |
|-----|--------|-------------|
| `homepage` | `/hive/config/homepage` (~42KB, 3 files / 2 dirs) | `/mnt/monarch/appdata/homepage` |
| `homepage-images` | `/hive/data/homepage/images` (empty, root-owned) | `/mnt/monarch/appdata/homepage/images` |

## Review checklist

| Check | Result |
|-------|--------|
| Source paths | Match live binds → `/app/config` and `/app/public/images` |
| Destination paths | Correct appdata targets |
| Exclusions | None |
| Compose file rewrite | **N/A** — repo already uses `${PATH_CONFIG}/homepage` and `${PATH_DATA}/homepage/images` (no literal `/hive/...` to sed) |
| Expected downtime | Brief stop per copy pass; final recreate after env align |
| Permissions | Config: `fatherfrank:fatherfrank`; images source: `root:root` empty (readable) |
| Live vs repo | Live managed from `/hive/homepage/`; authoritative target is `services/homepage/compose.yaml` + `services/.env` |

## Warnings (expected)

1. Source path string not found verbatim in compose — **EXPECTED** (PATH_* indirection)
2. Missing `services/.env` — **must create before execute restart** (gitignored)
3. Git working tree not clean — EXPECTED

## Alignment plan (not a compose sed)

1. Create gitignored `services/.env` with homepage-required vars; keep `PATH_*` on `/hive/config` + `/hive/data` during copy so post-copy restart stays on live paths.
2. Execute `homepage` copy, then `homepage-images` copy (no `--apply-compose`).
3. Cutover: stop → delta rsync both paths → set `PATH_CONFIG`/`PATH_DATA` to `/mnt/monarch/appdata` → `docker compose up -d` from `services/homepage`.
4. Rename sources to `.old`; rename `/hive/homepage` → `/hive/homepage.old`.

## Decision

**APPROVED** — execute copies sequentially; env align is the compose cutover for this service.
