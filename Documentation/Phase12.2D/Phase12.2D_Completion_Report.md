# Phase 12.2D — Completion Report

**Date:** 2026-07-31  
**Status:** Complete  
**Scope:** Prowlarr only

## Summary

Prowlarr migrated from CasaOS `/DATA/AppData/config` to `services/prowlarr/` + `/mnt/monarch/appdata/prowlarr`, dual-homed on `proxy`+`hotio`, Traefik labeled. Radarr integration URLs remediated to Docker DNS; Sonarr kept on host LAN (host-net exception).

## Outcomes

| Check | Result |
|---|---|
| Compose SoT | `services/prowlarr/compose.yml` |
| Image | `ghcr.io/hotio/prowlarr:release-2.3.5.5327` |
| Appdata | `/mnt/monarch/appdata/prowlarr` |
| Networks | `proxy` + `hotio_default` |
| Health | healthy |
| Indexers | **10** preserved |
| Sonarr app test | **PASS** |
| Radarr app test | **PASS** |
| ApplicationIndexerSync | **201** |
| forceSave Sonarr/Radarr | **202** |
| Traefik | `prowlarr.fatherfankscloud.uk` |

## Backup

`/hive/backups/prowlarr/pre-12.2D-20260731T142133`

## Explicitly not done

Sonarr re-home, Radarr changes, Jellyfin, Jellyseerr, Bazarr, Lidarr, downloaders, media.
