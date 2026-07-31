# Phase 12.2B — Sonarr Migration — Plan

**Date:** 2026-07-31  
**Status:** Complete  
**Scope:** Sonarr only (native systemd → Docker Phase 12 pattern)

## Objective

Migrate production Sonarr from mono/systemd into repo-managed Docker with appdata on Monarch.

## Source of truth (mandatory)

| Path | Role |
|---|---|
| `/var/lib/sonarr` | **Migration source** — 214 series, branch `main`, v3.0.10.1566 |
| `/hive/Hotio/sonarr` | **Abandoned** — 15 series, develop — **MUST NOT use** |

## Out of scope

Radarr, Jellyfin, Bazarr, Lidarr, media libraries, download data.

## Target

| Item | Path |
|---|---|
| App state | `/mnt/monarch/appdata/sonarr` |
| Compose SoT | `services/sonarr/` (`compose.yml` per Phase 12.1/12.2A naming) |
| Env | dedicated `.env` + committed `.env.example` |

## Image pin

`lscr.io/linuxserver/sonarr:version-3.0.10.1566` — matches native `ReleaseVersion=3.0.10.1566` (no v3→v4 DB upgrade in this phase).

## Networking decision

`network_mode: host` so existing download clients (`localhost:6789` NZBGet, `localhost:8080` qBittorrent) keep working without rewriting Sonarr DB settings.

## Path mounts (identity mapping)

- `/mnt/monarch/appdata/sonarr` → `/config`
- `/hive/jellyfin/tv` → `/hive/jellyfin/tv` (root folders unchanged)
- `/hive/downloads` → `/hive/downloads` (remote path local side unchanged)

Media and downloads stay on `/hive`.

## Procedure

1. Inventory + backup `/var/lib/sonarr`
2. Stop/disable systemd `sonarr`
3. Rsync state → `/mnt/monarch/appdata/sonarr` (ownership `fatherfrank:fatherfrank`)
4. Deploy `services/sonarr`
5. Validate UI, 214 series, clients, root folders
6. Document rollback + mark roadmap complete
