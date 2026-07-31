# Phase 12.4 — Platform Inventory

**Captured:** 2026-07-31 (pre/post standardized)

| Service | Before | After |
|---|---|---|
| **Jellyfin** | `services/jellyfin`, appdata, `proxy`, Traefik, `:latest`, `:8096`, `/dev/dri` | Pin `release-10.11.6`, limits, `traefik.docker.network=proxy`, `:8096` kept |
| **Jellyseerr** | CasaOS, `/DATA/...`, `hotio`+`jellyfin_default`, no Traefik, `:latest` | `services/jellyseerr`, `/mnt/monarch/appdata/jellyseerr`, `proxy` only, Traefik, digest pin |
| **Bazarr** | CasaOS, `/DATA/...`, `hotio` only, Radarr IP=`172.27.0.2` (self) | `services/bazarr`, appdata, `proxy`+`hotio`, Traefik, Radarr=`radarr` |
| **Lidarr** | Not installed | Out of scope |

## Backups

- Jellyseerr: `/hive/backups/jellyseerr/pre-12.4-*`
- Bazarr: `/hive/backups/bazarr/pre-12.4-*`
- Jellyfin: state already on Monarch (recreate-only; no data move)
