# Phase 11 — Batch 05 Summary (*arr download stack)

**Date:** 2026-07-30  
**Label:** User called this the “4th live migration batch”; prior Batch04 (Hermes/n8n/…) already exists under `Validation/Phase11/Batch04/`, so this write-up is stored as **Batch05** to avoid overwrite.

## Overall summary

Two of six targets completed successfully (NZBGet, Hotio). Batch **STOPPED** at Prowlarr because that service (and the three after it) are not registered in the Phase 10.5 migration framework.

## Services / execution order

| Order | Service | Result | Notes |
|---|---|---|---|
| 1 | NZBGet | **READY FOR SOAK** | Config → appdata; downloads/log excluded; `.old` retained |
| 2 | Hotio (qbittorrent) | **READY FOR SOAK** | VPN config migrated; NZBGet recreated after network namespace change |
| 3 | Prowlarr | **STOP** | Not in `services.conf`; no repo compose; CasaOS-managed |
| 4 | Radarr | Not started | Same blocker |
| 5 | Jellyseerr | Not started | Same blocker |
| 6 | Bazarr | Not started | Same blocker |

## Timings (approx.)

| Service | Copy size | Downtime |
|---|---|---|
| NZBGet | 1.3 MB (excludes 140 GB) | ~few minutes (+ checksum hang workaround) |
| Hotio | ~22 MB | ~1–2 minutes (+ NZBGet recreate) |

## Issues and resolutions

1. **NZBGet framework `--checksum` hung** — `verify-service.sh` checksums the full source including excluded 110 GB downloads + 30 GB log. Killed; completed exclude-aware checksum (10/10 match); finished compose apply + start manually.
2. **Hotio recreate broke NZBGet** — `network_mode: container:<old-qbittorrent-id>`. Resolved by recreating NZBGet from `services/NZBget/compose.yml`.
3. **Prowlarr+** — missing framework entries. Hard STOP; no ad-hoc migration.

## Outstanding warnings

- NZBGet image floated to **25.2** (unpinned `ghcr.io/hotio/nzbget`).
- Portainer compose/33 still references old NZBGet paths — live container is now repo-managed; tidy Portainer stack when convenient.
- `/hive/Hotio/compose.yml` still on disk; live Hotio is now started from `services/Hotio/compose.yml`.
- Do **not** run recursive `chown` on `/mnt/monarch/appdata` (see PostMigrationRemediation).

## Rollback summary

| Service | Rollback tree |
|---|---|
| NZBGet | `/hive/NZBget/config.old` |
| Hotio | `/hive/Hotio/config.old` |

## Recommended next actions

1. Author `services.conf` + `services/*/compose.yml` for Prowlarr, Radarr, Jellyseerr, Bazarr (CasaOS cutover plan).
2. Optionally migrate **Jellyfin** (already mapped, `order=40`) in a dedicated batch — media stays on hive.
3. Consider fixing `verify-service.sh` checksum to honour `rsync_excludes`.
4. Leave NZBGet/Hotio `.old` ≥ 7 days.

## Operator notes

- Batch is **partially** ready for soak: **NZBGet + Hotio only**.
- **Do not proceed** to Prowlarr/Radarr/Jellyseerr/Bazarr until framework entries exist.
- NZBGet and Hotio are interdependent via shared network namespace — treat them as a pair for any future recreate.
