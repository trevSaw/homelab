# Phase 12.2B — Completion Report

**Date:** 2026-07-31  
**Status:** Complete  
**Scope:** Sonarr only

## Summary

Native systemd/mono Sonarr (`/var/lib/sonarr`, v3.0.10.1566, 214 series) was migrated to Docker under `services/sonarr/` with app state on `/mnt/monarch/appdata/sonarr`. Abandoned `/hive/Hotio/sonarr` was not used.

## Outcomes

| Check | Result |
|---|---|
| Image | `lscr.io/linuxserver/sonarr:version-3.0.10.1566` |
| Health | healthy (`network_mode: host`) |
| Version / branch | `3.0.10.1566` / `main` |
| AppData | `/config` → `/mnt/monarch/appdata/sonarr` |
| Series | **214** |
| Root folders accessible | 7/8 (JDrama path missing on host — **pre-existing**) |
| Quality profiles | 10 |
| Indexers | 8 (RSS/search enabled) |
| NZBGet test | PASS (`localhost:6789`) |
| qBittorrent test | PASS (`localhost:8080`) |
| systemd | disabled / inactive |

## Backup

`/hive/backups/sonarr/native-20260731T135401` (DB md5 `fdf0431f98811c2484ef6f6d04eb2ce5`, 214 series)

## Explicitly not done

- Radarr / Bazarr / Lidarr / Jellyfin
- Media or download moves
- Sonarr v4 upgrade
- Enabling Sonarr authentication
- Fixing missing host path `/hive/jellyfin/tv/JDrama`

See `Validation/Phase12.2B/sonarr/` and `Known_Exceptions.md`.
