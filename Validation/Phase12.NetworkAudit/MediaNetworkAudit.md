# Media Network Compliance Audit

**Date:** 2026-07-31  
**Scope:** Read-only validation against `Architecture/media-stack-networking.md`  
**Host:** mocha  
**Rule:** No containers modified, recreated, or restarted

## Verdict (executive)

| Outcome | Count | Services |
|---|---|---|
| **PASS** | 2 | Traefik, qBittorrent (network membership) |
| **WARNING** | 7 | Jellyfin, Sonarr, Prowlarr, Bazarr, NZBGet, Jellyseerr (Overseerr stand-in), qBittorrent (host ports) |
| **FAIL** | 1 | Radarr (broken download-client endpoints + missing `proxy`) |
| **N/A** | 2 | Lidarr (not deployed), Overseerr brand (Jellyseerr deployed instead) |

**Related / out of canonical membership (noted only):** Readarr, Byparr — on `hotio_default`, not in the architecture membership table.

## Architecture under test

| Network | Live Docker name | Role |
|---|---|---|
| `proxy` | `proxy` | Traefik ingress / user-facing |
| `hotio` | `hotio_default` | Automation DNS |

## Already compliant

- **Traefik** — on `proxy` only; publishes `80`/`443` (required edge exception).
- **qBittorrent** — on `hotio_default` only (membership PASS). Host ports remain a separate WARNING.

## Needs one additional network (`proxy`)

Dual-homed targets currently on `hotio` only:

- Radarr
- Prowlarr
- Bazarr

(Also fix Radarr client hosts before relying on DNS.)

## Should lose host networking

- **Sonarr** — `network_mode: host`; download clients use `localhost`. Target: dual-home `proxy` + `hotio`, then switch clients to `qbittorrent` / `nzbget` (or interim `qbittorrent:6789` while NZBGet shares VPN netns).

## Already has Traefik integration

| Service | Traefik | Notes |
|---|---|---|
| Traefik | Yes (dashboard) | `traefik.fatherfankscloud.uk` |
| Jellyfin | Yes | `jellyfin.fatherfankscloud.uk` + still publishes host `:8096` |
| Sonarr | No | |
| Radarr | No | |
| Prowlarr | No | |
| Bazarr | No | |
| Jellyseerr | No | |
| qBittorrent / NZBGet | No | Expected (hotio-only) |

## Unnecessary / transitional host ports

| Service | Host ports | Note |
|---|---|---|
| Jellyfin | `8096` | Redundant once Traefik-only access is enforced |
| Radarr | `7878` | Should move to Traefik after `proxy` attach |
| Prowlarr | `9696` | Same |
| Bazarr | `6767` | Same |
| Jellyseerr | `5055` | Should be `proxy` + Traefik (Overseerr role) |
| qBittorrent | `8080`, `8118`, `6789` | `6789` currently fronts NZBGet via shared netns; UI ports are operator convenience |
| Traefik | `80`, `443` | Required — not unnecessary |

## Critical finding

**Radarr download clients point at `172.27.0.7` (Radarr’s own `hotio` IP)** for both NZBGet `:6789` and qBittorrent `:8080`. Live qBittorrent is `172.27.0.4`. From the host, `.7:8080` does not answer; `.4:8080` / `.4:6789` do. This is a **broken dependency** (FAIL), independent of Traefik.

## Artifacts

- `ContainerInventory.md` — per-container facts  
- `ComplianceMatrix.md` — expected vs actual  
- `RecommendedMigrationOrder.md` — suggested sequence (no execution)
