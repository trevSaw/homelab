# Compliance Matrix — Media Networks

**Date:** 2026-07-31  
**Standard:** `Architecture/media-stack-networking.md`

| Service | Current Networks | Expected Networks | Status | Action Required |
|---|---|---|---|---|
| Traefik | `proxy` | `proxy` | **PASS** | None (keep host `80`/`443`) |
| Jellyfin | `proxy` | `proxy` | **WARNING** | Drop host `:8096` when Traefik-only access is accepted; pin image later (out of band) |
| Sonarr | `host` | `proxy` + `hotio` | **WARNING** | Leave host net; dual-home; change clients off `localhost`; add Traefik; remove host mode |
| Radarr | `hotio_default` | `proxy` + `hotio` | **FAIL** | Fix download-client hosts (currently self-IP `172.27.0.7`); add `proxy` + Traefik; drop `:7878` when routed; move SoT/appdata in Phase 12 migration |
| Prowlarr | `hotio_default` | `proxy` + `hotio` | **WARNING** | Add `proxy` + Traefik; drop `:9696` when routed; standardize compose/appdata |
| Bazarr | `hotio_default` | `proxy` + `hotio` | **WARNING** | Add `proxy` + Traefik; drop `:6767` when routed; standardize compose/appdata |
| Lidarr | _(not deployed)_ | `proxy` + `hotio` | **N/A** | Deploy only to canonical pattern if introduced |
| Overseerr | _(not deployed)_ | `proxy` | **N/A** | — |
| Jellyseerr *(Overseerr role)* | `hotio_default`, `jellyfin_default` | `proxy` | **WARNING** | Move to `proxy` (+ Traefik); remove `hotio` / `jellyfin_default` unless a documented exception needs Docker DNS to Jellyfin/*arr |
| qBittorrent | `hotio_default` | `hotio` | **PASS** | Membership OK; see host-port WARNING in audit notes |
| NZBGet | _(via qBittorrent netns)_ | `hotio` | **WARNING** | No first-class DNS name; keep VPN sharing until dedicated redesign; clients should use `qbittorrent:6789` on `hotio` |

## Status definitions used

| Status | Meaning |
|---|---|
| **PASS** | Matches architecture for required network membership |
| **WARNING** | Working (or partially working) but not aligned — host net, missing network, host ports, shared netns, wrong extra networks |
| **FAIL** | Architecture / dependency violation needing remediation (broken client endpoints, isolation from required peers) |
| **N/A** | Not deployed |

## Quick filters

### Already comply (membership)

- Traefik  
- qBittorrent  

### Need one additional network (`proxy`)

- Radarr  
- Prowlarr  
- Bazarr  

### Should lose host networking

- Sonarr  

### Traefik present today

- Traefik (dashboard)  
- Jellyfin  

### Host ports still exposed (media UIs / helpers)

- Jellyfin `:8096`  
- Radarr `:7878`  
- Prowlarr `:9696`  
- Bazarr `:6767`  
- Jellyseerr `:5055`  
- qBittorrent `:8080`, `:8118`, `:6789` (NZBGet front)
