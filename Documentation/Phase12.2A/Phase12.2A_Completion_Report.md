# Phase 12.2A — Completion Report

**Date:** 2026-07-31  
**Status:** Complete  
**Scope:** qBittorrent (Hotio), NZBGet  
**SABnzbd:** Not present / not used — excluded

## Summary

Both download clients were already on `/mnt/monarch/appdata` from Phase 11. Phase 12.2A standardized compose SoT to the Phase 12.1 pattern: pinned images, `.env` / `.env.example`, healthchecks, resource limits, and documented exceptions. Downloads remain on `/hive`.

## Outcomes

| Service | Image pin | Config | Result |
|---|---|---|---|
| qBittorrent (Hotio) | `ghcr.io/hotio/qbittorrent:release-4.5.5` | `/mnt/monarch/appdata/hotio` | healthy; WebUI `:8080` → 200 |
| NZBGet | `ghcr.io/hotio/nzbget@sha256:6815d7e…` (25.2) | `/mnt/monarch/appdata/nzbget` | healthy; WebUI `:6789` → 401 (auth) |
| SABnzbd | — | — | Absent; out of scope |

## Key changes

- Left `cr.hotio.dev` (DNS unreliable on host) for `ghcr.io/hotio/qbittorrent:release-4.5.5` — same app version 4.5.5, no 5.x jump
- NZBGet pinned to exact prior digest (avoids floating `:latest`)
- Env moved into dedicated per-service `.env` (not shared `services/.env`)
- NZBGet `TZ` normalized `Denver` → `America/Denver`
- Memory limits set to readable `8G` / `4G` (were multi‑GB byte strings)

## Recreate order used

1. `services/Hotio` → `docker compose up -d --force-recreate`
2. `services/NZBget` → `docker compose up -d --force-recreate`

## Validation

See `Validation/Phase12.2A/hotio/` and `Validation/Phase12.2A/nzbget/`.

## Explicitly not done

- Sonarr / Radarr / Jellyfin / media libraries
- Moving downloads off `/hive`
- qBittorrent 5.x upgrade
- Renaming `Hotio` → `qbittorrent`
- SABnzbd
