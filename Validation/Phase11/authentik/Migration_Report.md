# Phase 11 — Authentik Migration Report

**Service:** authentik  
**Batch:** 02  
**Final status:** READY FOR SOAK  
**Completed:** 2026-07-30T10:42:00Z

## Summary

Authentik state migrated from `/hive/data/authentik` → `/mnt/monarch/appdata/authentik` using docker-root rsync (preserve Postgres uid 70). Cutover via `PATH_DATA=/mnt/monarch/appdata` in gitignored `services/.env`. Stack started from `services/authentic/compose.yaml`.

## Paths

| Role | Path |
|------|------|
| Source (rollback) | `/hive/data/authentik.old` |
| Old compose project | `/hive/authentic.old` |
| Destination | `/mnt/monarch/appdata/authentik` |
| Authoritative compose | `services/authentic/compose.yaml` |
| Env (gitignored) | `services/.env` (+ `services/authentic/.env` symlink) |

## Compose / env change

- No literal volume sed (PATH_* already in compose).
- `services.conf` remapped: source=`/hive/data/authentik`, `migration_required=yes`.
- Healthcheck updated (wget → Python) so Traefik does not filter the server.

## Verification

- Root rsync: 3092 files / 33 dirs / 88.7MB  
- Root checksum inventory: **MATCH**  
- Evidence: `reports/verify-authentik-root.txt`, `reports/verify-authentik.json`

## Smoke

See `Smoke_Test.md`.

## Rollback

```bash
(cd services/authentic && docker compose -f compose.yaml down)
# Restore data name
docker run --rm -v /hive/data:/data alpine:3.20 \
  mv /data/authentik.old /data/authentik
# Point PATH_DATA back to /hive/data in services/.env (or use /hive/authentic.old)
mv /hive/authentic.old /hive/authentic
# Start from hive project with PATH_DATA=/hive/data
```

Keep `.old` ≥ **7 days**. Do not delete automatically.

## Lessons learned

1. Authentik was mis-classified as verify/partial with empty source; live data was under `/hive/data/authentik`.
2. User-level rsync cannot preserve uid 70 Postgres ownership — use root/docker-root copy.
3. Traefik docker provider skips unhealthy containers; a broken healthcheck becomes an outage.

## Final decision

**READY FOR SOAK**
