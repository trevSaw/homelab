# Phase 12.3 — Compliance Matrix

**Date:** 2026-07-31  
**Standard:** `Architecture/media-stack-networking.md` + Phase 12 compose pattern

| Service | Repo SoT | Appdata | Networks | Traefik | DNS clients | Status | Notes |
|---|---|---|---|---|---|---|---|
| Traefik | yes | ACME on monarch | `proxy` | self | n/a | **PASS** | Edge `80`/`443` required |
| qBittorrent | yes | `/mnt/monarch/appdata/hotio` | `hotio` | no (expected) | n/a | **PASS** | Host ports for UI/VPN publish |
| NZBGet | yes | `/mnt/monarch/appdata/nzbget` | via qBittorrent netns | no (expected) | n/a | **PASS (Documented Exception)** | No `nzbget` DNS name; use `qbittorrent:6789` |
| Radarr | yes | `/mnt/monarch/appdata/radarr` | `proxy`+`hotio` | yes | `qbittorrent` | **PASS (Documented Exception)** | Transitional host `:7878` |
| Prowlarr | yes | `/mnt/monarch/appdata/prowlarr` | `proxy`+`hotio` | yes | `radarr` + LAN→Sonarr | **PASS (Documented Exception)** | Transitional `:9696`; Sonarr via LAN |
| Sonarr | yes | `/mnt/monarch/appdata/sonarr` | **host** | no | `localhost` | **PASS (Documented Exception)** | Dual-home + Traefik still owed |
| Jellyfin | yes (partial) | appdata | `proxy` | yes | n/a | **WARNING** | Consumption layer; `:latest`, host `:8096` |
| Jellyseerr | CasaOS | `/DATA/...` | `hotio`+`jellyfin_default` | no | n/a | **WARNING** | Not Phase 12 standardized; wrong nets vs Overseerr role |

### Status key

| Status | Meaning |
|---|---|
| **PASS** | Matches architecture for this baseline |
| **PASS (Documented Exception)** | Works; intentional/known gap recorded |
| **WARNING** | Outside automation baseline or incomplete standardization |
| **FAIL** | Broken dependency or architecture violation |

No **FAIL** items remain in the automation set after Phase 12.2C remediation.
