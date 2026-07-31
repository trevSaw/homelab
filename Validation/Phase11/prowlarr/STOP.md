# Prowlarr — STOP

**Date:** 2026-07-30  
**Decision:** **STOP** — do not continue to Radarr / Jellyseerr / Bazarr

## Why

Phase 10.5 requires every migration to go through `scripts/migration/services.conf` and a repo compose under `services/`. Prowlarr fails both prerequisites:

| Requirement | Prowlarr status |
|---|---|
| Entry in `services.conf` | **Missing** |
| Repo compose under `services/` | **Missing** |
| Live management | CasaOS: `/var/lib/casaos/apps/glorious_thomas/docker-compose.yml` |
| Live config bind | `/DATA/AppData/config` → `/config` (resolves under `/hive/AppData/config`, **15 MB**) |
| Image | `ghcr.io/hotio/prowlarr:latest` |

The framework cannot invent source/target/exclude/compose mappings safely. Doing so ad hoc would violate “Follow [the Phase 10.5 framework] exactly” and risks copying the wrong tree (note: Prowlarr’s path is the generic `/DATA/AppData/config`, not a service-named directory).

## Same blocker for remaining batch targets

| Service | services.conf | Repo compose | Live config |
|---|---|---|---|
| **Prowlarr** | no | no | `/DATA/AppData/config` (~15 MB) |
| **Radarr** | no | no | `/DATA/AppData/radarr/config` (~369 MB) |
| **Jellyseerr** | no | no | `/DATA/AppData/jellyseerr/config` (~2.1 MB) |
| **Bazarr** | no | no | `/DATA/AppData/bazarr/config` (~16 MB) |

All four are CasaOS-managed. None are in the migration map. **Jellyfin** *is* in `services.conf` (`order=40`) but was **not** in this batch’s target list.

## Operator actions required before resume

1. Add `services.conf` rows for each service (source, target `/mnt/monarch/appdata/<name>`, excludes, keep_hive media mounts).
2. Create `services/<name>/compose.yml` (or adopt CasaOS compose into the repo) with Traefik/network labels as desired.
3. Decide whether Prowlarr’s oddly generic `/DATA/AppData/config` path should move to `/mnt/monarch/appdata/prowlarr` (recommended) and update CasaOS or cut over to the repo project.
4. Re-run this batch from **Prowlarr** only after the above is reviewed.

## Batch progress so far

| # | Service | Status |
|---|---|---|
| 1 | NZBGet | **READY FOR SOAK** |
| 2 | Hotio | **READY FOR SOAK** |
| 3 | Prowlarr | **STOP** |
| 4–6 | Radarr / Jellyseerr / Bazarr | **Not started** (blocked) |
