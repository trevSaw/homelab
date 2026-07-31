# Phase 11 — Authentik Dry-Run Review

**Generated:** 2026-07-30T10:02:00Z  
**Status:** APPROVED — proceed with **docker-root rsync** (not user rsync)  
**Mode:** Framework `--dry-run` + remapped `services.conf`

## Remap applied

```text
source=/hive/data/authentik
target=/mnt/monarch/appdata/authentik
migration_required=yes
already_migrated=no
```

## Review checklist

| Check | Result |
|-------|--------|
| Source path | `/hive/data/authentik` — matches historical `PATH_DATA=/hive/data` tree (db/redis/media/certs/templates) |
| Destination | `/mnt/monarch/appdata/authentik` |
| Exclusions | None |
| Compose sed | N/A — repo already uses `${PATH_DATA}/authentik/*`; `services/.env` has `PATH_DATA=/mnt/monarch/appdata` |
| Stack state | Stopped (no containers) — low cutover risk |
| Permissions | `db/` is `0700` uid `70` — **host user cannot rsync**; must preserve uid 70 on dest |
| Ownership risk | User-level `rsync -a` would chown DB to `fatherfrank` and break Postgres |

## Expected warnings

- Partial tree stats / rsync dry-run non-zero under `db/` — EXPECTED without root
- Compose source string not found verbatim — EXPECTED (PATH_* )

## Copy method (approved exception)

Because framework `copy-config.sh` runs as the migration user, Authentik copy will use:

```bash
docker run --rm \
  -v /hive/data/authentik:/src:ro \
  -v /mnt/monarch/appdata/authentik:/dst \
  instrumentisto/rsync-ssh \
  rsync -aHAX /src/ /dst/
```

(or equivalent root rsync container). Checksums compared inside the same root context.

## Decision

**APPROVED** — docker-root copy → root verify → start `services/authentic` → smoke → `.old`.
