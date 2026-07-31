# Phase 12.2D — Prowlarr Migration — Plan

**Date:** 2026-07-31  
**Status:** Complete  
**Scope:** Prowlarr only

## Objective

Migrate Prowlarr to Phase 12 Docker SoT (same pattern as 12.2B/12.2C), dual-home on `proxy`+`hotio`, Traefik labels, preserve indexers and app integrations.

## Source

| Item | Value |
|---|---|
| Type | Docker (CasaOS `glorious_thomas`) |
| Data | `/DATA/AppData/config` |
| Image | `ghcr.io/hotio/prowlarr:latest` → 2.3.5.5327 |
| Network | `hotio_default` only |
| Indexers | 10 |
| Apps | Sonarr, Radarr |

## Target

| Item | Value |
|---|---|
| Compose | `services/prowlarr/compose.yml` |
| Appdata | `/mnt/monarch/appdata/prowlarr` |
| Image | `ghcr.io/hotio/prowlarr:release-2.3.5.5327` |
| Networks | `proxy` + `hotio` |
| Traefik | `prowlarr.fatherfankscloud.uk` |

## Out of scope

Sonarr, Radarr, Jellyfin, Jellyseerr, downloaders, Bazarr, Lidarr, media.
