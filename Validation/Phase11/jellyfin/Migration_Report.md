# Jellyfin — Migration Report

**Date:** 2026-07-31  
**Final decision:** **READY FOR SOAK**

## Summary

Jellyfin configuration migrated from `/hive/jellyfin/config` → `/mnt/monarch/appdata/jellyfin` using the patched Phase 10.5 framework. Ephemeral runtime trees were excluded. Media libraries remain on hive. Cutover complete; original config retained as `.old`.

| Path | Location |
|---|---|
| Live config | `/mnt/monarch/appdata/jellyfin` (**7.0 GB**, 41,099 verified files) |
| Rollback source | `/hive/jellyfin/config.old` (**9.0 GB**, includes excluded cache/transcodes/logs) |
| Media (unchanged) | `/hive/jellyfin/tv`, `/hive/jellyfin/movie` |
| Compose | `services/jellyfin/compose.yml` |

## Phase 1 — Policy

`services.conf` excludes (ephemeral only):

```
cache/**
data/transcodes/**
.temp/**
log/**
```

Retained: `data/data/**`, `data/metadata/**`, `data/plugins/**`, `data/root/**`, `dlna/**`, `.aspnet/**`, `system.xml`, `encoding.xml`, all `*.db` / `*.db-wal` / `*.db-shm`.

## Execution timeline (UTC)

| Step | Result |
|---|---|
| Framework checksum locale fix | Already resolved + 24/24 regression tests |
| Update `services.conf` excludes | SUCCESS |
| Remove stale staged copy | SUCCESS |
| Confirm source intact | SUCCESS (`jellyfin.db`, `system.xml`, metadata present) |
| Stop container | SUCCESS (SQLite checkpointed; WAL/SHM cleared) |
| Fresh rsync copy | SUCCESS — migratable **7.0 GB** |
| Patched `--checksum` verify | **PASS** — 41,099 matched, missing=0 changed=0 extra=0 |
| Compose apply | SUCCESS (after staging `.env` into proposed dir for validation) |
| Start + health | SUCCESS — healthy, `/health` HTTP 200 |
| Functional smoke | PASS (users, userdata, playback history, metadata, plugins, libraries) |
| Rename source → `.old` | SUCCESS |

## Files copied / excluded

| Category | Count / size |
|---|---|
| Copied + checksum-verified | **41,099 files** / **7.0 GB** |
| Excluded from source (left in `.old`) | cache 6,573 files; transcodes 444 files; log 24 files; `.temp` 1 file (~3.5 GB total) |
| Post-start runtime dirs recreated empty on dest | `cache/`, `data/transcodes/`, `log/` (expected; Jellyfin creates them) |

## Verification

```
INFO: Inventory records: source=41099 dest=41099
INFO: Checksum inventory matches: 41099 file(s) identical (missing=0 changed=0 extra=0)
```

Prior abort failure was a framework locale/sort bug — fixed and documented in [Framework_Fix_Checksum_Locale.md](../Framework_Fix_Checksum_Locale.md).

## Compose diff applied

```diff
-      - /hive/jellyfin/config:/config
+      - /mnt/monarch/appdata/jellyfin:/config
```

TV/movie mounts, ports, Traefik labels, `/dev/dri`, and NVIDIA env unchanged.  
Backup: `Validation/Phase11/jellyfin/proposed/jellyfin/compose.yml.pre-migrate.bak`

## Smoke test results

| Check | Result |
|---|---|
| Container | running / **healthy** |
| `GET /health` | **Healthy** (HTTP 200) |
| Mounts | `/mnt/monarch/appdata/jellyfin` → `/config`; media still on hive |
| Users | `fatherfrank`, `test` (2) |
| Watch / userdata | `UserData` **19,809** rows; Playback Reporting **444** activities |
| Metadata / artwork | **24,573** files under `data/metadata` (People/library/Studio/…) |
| Plugins | AniDB, Fanart, Kodi Sync Queue, Open Subtitles, Playback Reporting, Session Cleaner, TMDb Box Sets |
| Libraries | Anime, Cartoons, Collections, Drama, Fantasy, KDramas, Movies, … under `data/root/default` |
| Public system info | Version **10.11.6**, `StartupWizardCompleted=true` |
| Recent logs | No error/exception/fatal lines in first 5 minutes |

## Rollback

```bash
cd /home/fatherfrank/projects/homelab/services/jellyfin
docker compose stop
# restore compose from backup OR revert volume source to /hive/jellyfin/config
mv /hive/jellyfin/config.old /hive/jellyfin/config
# point compose volume back to /hive/jellyfin/config, then:
docker compose up -d
```

Keep `/hive/jellyfin/config.old` ≥ **7 days**. Do not delete automatically.

## Lessons learned

1. Locale-sensitive checksum sort is fixed; future migrations benefit automatically.
2. Ephemeral Jellyfin trees (`cache`, `transcodes`, `.temp`, `log`) should stay excluded — ~3.5 GB saved, zero durable state lost.
3. `update-compose.sh` must stage `.env` into the proposed directory for validation; fixed during this cutover.
4. Stop the container before copy so SQLite WAL is checkpointed into `jellyfin.db`.

## Commands (abbreviated)

```bash
# policy
# services.conf: rsync_excludes=cache/**,data/transcodes/**,.temp/**,log/**

rm -rf /mnt/monarch/appdata/jellyfin
docker stop jellyfin
PHASE_DIR=Validation/Phase11/jellyfin ./scripts/migration/run-migration.sh --execute --apply-compose --checksum jellyfin
# (compose apply retried after .env staging fix)
PHASE_DIR=Validation/Phase11/jellyfin ./scripts/migration/update-compose.sh --execute --apply-compose jellyfin
cd services/jellyfin && docker compose up -d
mv /hive/jellyfin/config /hive/jellyfin/config.old
```

## Status

**READY FOR SOAK** — leave `.old` untouched for a minimum of seven (7) days before cleanup.
