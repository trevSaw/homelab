# Phase 12.2A — Media Download Infrastructure — Plan

**Date:** 2026-07-31  
**Status:** Complete  
**Scope:** qBittorrent (Hotio) and NZBGet only

## Objective

Apply the Phase 12.1 production Docker pattern to the download clients that already live on `/mnt/monarch/appdata`. This is **standardization**, not a hive→appdata data migration.

## In scope

| Service | Role | Compose SoT | Config | Downloads |
|---|---|---|---|---|
| qBittorrent (Hotio) | BitTorrent + VPN gateway | `services/Hotio/` | `/mnt/monarch/appdata/hotio` | `/hive/downloads/completed` |
| NZBGet | Usenet client | `services/NZBget/` | `/mnt/monarch/appdata/nzbget` | `/hive/downloads` |

## Out of scope (explicit)

- **SABnzbd** — not used on this host; absent; do not migrate or invent
- Sonarr, Radarr, Lidarr, Prowlarr, Jellyfin
- Media libraries under `/hive`
- Moving download/incomplete paths off `/hive`
- qBittorrent major upgrade (4.5.5 → 5.x)

## Canonical pattern (from 12.1)

- Compose SoT: git `services/<service>/`
- Persistent config: `/mnt/monarch/appdata/<service>`
- Committed `.env.example`; live `.env` gitignored
- Pinned image tags (no floating `latest` / untagged)
- `restart: unless-stopped`
- Healthchecks where feasible; document exemptions
- `deploy.resources.limits.memory` set
- Document security / networking exceptions

## Image pins (no major version jump)

| Service | Before | After |
|---|---|---|
| qBittorrent | `cr.hotio.dev/hotio/qbittorrent:latest` (label 4.5.5; registry DNS unreliable) | `ghcr.io/hotio/qbittorrent:release-4.5.5` |
| NZBGet | `ghcr.io/hotio/nzbget` (untagged → latest; label 25.2) | `ghcr.io/hotio/nzbget@sha256:6815d7e4837b1b03771465ec67191a94e4eb67ebfdc7322d3394ebf8952eb879` (25.2, exact live digest) |

## Critical dependency

NZBGet uses `network_mode: container:qbittorrent` so it shares the Hotio VPN network namespace and published ports (`6789` via Hotio).

**Recreate order:** qbittorrent first, then nzbget. Recreating Hotio alone leaves NZBGet broken until NZBGet is recreated.

## Success criteria

- Both stacks launched from repo compose with pins + `.env.example`
- Config still on appdata; downloads still on `/hive`
- WebUI smoke: qBittorrent `:8080`, NZBGet `:6789`
- SABnzbd documented as not present
- Validation under `Validation/Phase12.2A/`
- Roadmap: Phase 12.2A Complete
