# Phase 11 — Calibre Dry-Run Review

**Generated:** 2026-07-30T10:51:30Z  
**Status:** APPROVED — proceed to execute copy  
**Mode:** `--dry-run` only

## Review checklist

| Check | Result |
|-------|--------|
| Source | `/hive/calibre/config` (~37MB, 312 files) — matches live `/config` |
| Destination | `/mnt/monarch/appdata/calibre` |
| Exclusions | None |
| Keep on hive | `/hive/library` (books + browser_cache binds unchanged) |
| Compose diff | Single rewrite: `/hive/calibre/config` → `/mnt/monarch/appdata/calibre` |
| Unrelated services | calibre-web volume lines untouched; books path untouched |
| Shared compose | `services/calibre-web/compose.yml` — only calibre service path changed |
| Expected downtime | Brief stop of calibre during copy |

## Decision

**APPROVED** — execute copy without `--apply-compose`, then cutover sync + apply.
