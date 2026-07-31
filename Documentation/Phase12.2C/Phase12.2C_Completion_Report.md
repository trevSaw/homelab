# Phase 12.2C — Completion Report

**Date:** 2026-07-31  
**Status:** Complete  
**Scope:** Radarr only

## Summary

Radarr was migrated from CasaOS/`/DATA/AppData/radarr` to repo-managed `services/radarr/` with appdata on `/mnt/monarch/appdata/radarr`, dual-homed on `proxy` + `hotio`, and download clients remediated to Docker DNS.

## Outcomes

| Check | Result |
|---|---|
| Compose SoT | `services/radarr/compose.yml` |
| Image pin | `ghcr.io/hotio/radarr:release-5.22.4.9896` |
| Appdata | `/mnt/monarch/appdata/radarr` |
| Networks | `proxy` + `hotio_default` |
| Health | healthy |
| Movies | **231** preserved |
| Root folder `/movies` | accessible |
| qBittorrent test | **PASS** (`qbittorrent:8080`) |
| NZBGet test | **PASS** (`qbittorrent:6789`) |
| Prior FAIL (self-IP `172.27.0.7`) | **Resolved** |
| Traefik labels | enabled (`radarr.fatherfankscloud.uk`) |

## Backup

`/hive/backups/radarr/pre-12.2C-20260731T141538` (231 movies)

## Explicitly not done

Sonarr, Prowlarr, Jellyfin, Bazarr, Lidarr, downloaders, media moves.
