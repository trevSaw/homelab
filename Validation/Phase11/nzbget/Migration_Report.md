# NZBGet — Migration Report

**Date:** 2026-07-30  
**Final decision:** **READY FOR SOAK**

## Summary

NZBGet configuration migrated from `/hive/NZBget/config` to `/mnt/monarch/appdata/nzbget`. Nested downloads (~110 GB) and `nzbget.log` (~30 GB) were excluded and remain on hive under `.old`. Active downloads continue via `/hive/downloads`. Compose volume for `/config` rewritten; `/hive/downloads` and `network_mode: container:qbittorrent` unchanged.

| Path | Location |
|---|---|
| New config | `/mnt/monarch/appdata/nzbget` (1.3 MB) |
| Rollback source | `/hive/NZBget/config.old` (~120 GB incl. nested downloads + log) |
| Downloads (live) | `/hive/downloads` |
| Compose | `services/NZBget/compose.yml` |

## Execution timeline (UTC)

| Step | Result |
|---|---|
| Dry-run | SUCCESS — migratable 1.3 MB after excludes |
| Review | APPROVED (`Dry_Run_Review.md`) |
| Stop container | SUCCESS |
| rsync copy | SUCCESS — 10 files, 1,259,140 bytes |
| Framework `--checksum` | **HUNG** — `verify-service.sh` checksums entire source including excluded 140 GB tree |
| Manual excluded checksum | **MATCH** — 10/10 files identical |
| Apply compose | SUCCESS |
| Start (`docker compose up -d`) | SUCCESS |
| Smoke test | PASS (WebUI 401 auth) |
| Rename source → `.old` | SUCCESS |

## Verification

- Dest size 1.3 MB; empty `downloads/` dir only (0 files); no `nzbget.log`.
- Checksums of all migratable files match source.
- Ownership `1000:1000` after container start (Hotio PUID/PGID apply).

## Compose diff applied

```diff
-        source: /hive/NZBget/config
+        source: /mnt/monarch/appdata/nzbget
```

Backup: `Validation/Phase11/nzbget/proposed/nzbget/compose.yml.pre-migrate.bak`

## Rollback

```bash
cd /home/fatherfrank/projects/homelab/services/NZBget
docker compose stop
# restore compose from backup OR revert volume source to /hive/NZBget/config
mv /hive/NZBget/config.old /hive/NZBget/config
# point compose volume back to /hive/NZBget/config, then:
docker compose up -d
# Or restart prior Portainer stack compose/33 after path restore
```

Keep `/hive/NZBget/config.old` ≥ **7 days**. Do not delete automatically.

## Lessons learned

1. Framework `--checksum` does **not** honour `rsync_excludes` — unsafe/impractical for trees with large excluded datasets. For NZBGet, verify with an exclude-aware checksum instead.
2. Pre-creating only `/mnt/monarch/appdata/nzbget` (not tree-wide chown) avoids collateral ownership damage.
3. NZBGet depends on qbittorrent network namespace — do not stop Hotio while NZBGet is expected to serve its UI.
4. Live was Portainer project 33; repo compose now owns the running container.

## Commands (abbreviated)

```bash
PHASE_DIR=Validation/Phase11/nzbget ./scripts/migration/run-migration.sh --dry-run --checksum nzbget
install -d -o fatherfrank -g fatherfrank /mnt/monarch/appdata/nzbget
PHASE_DIR=Validation/Phase11/nzbget ./scripts/migration/run-migration.sh --execute --apply-compose --checksum nzbget
# (killed hung checksum; manual exclude-aware cksum; then)
PHASE_DIR=Validation/Phase11/nzbget ./scripts/migration/update-compose.sh --execute --apply-compose nzbget
cd services/NZBget && docker compose up -d
mv /hive/NZBget/config /hive/NZBget/config.old
```
