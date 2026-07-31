# Phase 11 — Traefik Dry-Run Review

**Generated:** 2026-07-30T10:57:30Z  
**Status:** APPROVED — **verify-only** (no copy / no Traefik recreate)  
**Mode:** `--dry-run`

## Framework classification

| Field | Value |
|-------|-------|
| `migration_required` | `verify` |
| `already_migrated` | `partial` |
| Source | *(none)* |
| Destination | `/mnt/monarch/appdata/traefik` |

## Live confirmation

| Check | Result |
|-------|--------|
| Live acme mount | `/mnt/monarch/appdata/traefik/acme.json` → `/etc/traefik/acme.json` ✓ |
| Destination present | yes (`acme.json` 31KB, newer than hive leftover) |
| Compose project | Still managed from `/hive/traefik/compose.yaml` |
| Hive leftover | `/hive/config/traefik/acme.json` (stale Feb 11; not live-mounted) |
| Copy required | **no** |
| Compose sed | N/A — already `${PATH_CONFIG}/traefik/acme.json` |

## Safety decision on restart

Full `run-migration.sh --execute` would `docker compose up -d` from `services/traefik` **without stopping first** (verify ≠ yes), recreating the edge proxy. That is unnecessary for verify-only and high blast radius.

**Execute plan:** inventory + destination verify + functional smoke through existing Traefik. **Do not** recreate Traefik. Optionally rename stale `/hive/config/traefik` → `.old`.

## Decision

**APPROVED** — verify-only path as above.
