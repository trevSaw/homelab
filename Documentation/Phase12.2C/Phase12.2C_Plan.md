# Phase 12.2C — Radarr Migration & Network Remediation — Plan

**Date:** 2026-07-31  
**Status:** Complete  
**Scope:** Radarr only

## Objective

Migrate Radarr to Phase 12 Docker SoT and fix the audit FAIL (download clients pointing at Radarr’s own IP).

## Source (inventory)

| Item | Value |
|---|---|
| Type | Docker (CasaOS-managed historically) |
| Image before | `ghcr.io/hotio/radarr:latest` → 5.22.4.9896 |
| Data | `/DATA/AppData/radarr/config` |
| Networks | `hotio_default` only |
| Movies | 231 |
| FAIL | Download clients host `172.27.0.7` (self) |

## Target

| Item | Value |
|---|---|
| Compose | `services/radarr/compose.yml` |
| Appdata | `/mnt/monarch/appdata/radarr` |
| Image | `ghcr.io/hotio/radarr:release-5.22.4.9896` |
| Networks | `proxy` + `hotio` (`hotio_default`) |
| Clients | `qbittorrent:8080`, `qbittorrent:6789` |

## Out of scope

Sonarr, Prowlarr, Jellyfin, Bazarr, Lidarr, qBittorrent, NZBGet, media libraries.
