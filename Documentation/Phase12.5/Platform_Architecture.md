# Platform Architecture — Phase 12 Closeout

## Core Infrastructure

**Purpose:** Edge ingress, identity, container management, baseline observability.

| Service | Role |
|---|---|
| Traefik | HTTPS reverse proxy |
| Authentik (+ db/redis) | SSO / identity |
| Portainer | Container management UI |
| Beszel + agent | Host/container monitoring |
| Uptime Kuma | Uptime checks |
| Homepage | Portal (present) |

## Media Automation

**Purpose:** Acquire and organize media via indexers + download clients + *arr.

| Service | Role |
|---|---|
| Prowlarr | Indexer manager |
| Sonarr | TV automation |
| Radarr | Movie automation |
| qBittorrent (Hotio) | Torrents + VPN gateway |
| NZBGet | Usenet (VPN via qBittorrent netns) |
| Byparr / Readarr | Related helpers (partially standardized) |

## Media Consumption

**Purpose:** User-facing playback and requests.

| Service | Role |
|---|---|
| Jellyfin | Media server |
| Jellyseerr | Request UI |
| Bazarr | Subtitles |

## Storage

**Purpose:** Persist app state on SSD (Monarch); bulk content on Hive.

See `Storage_Architecture.md`.

## Monitoring

Overlaps Core: Beszel, Uptime Kuma; plus service healthchecks.

## Development

| Service | Role |
|---|---|
| code-server | Browser IDE |
| n8n | Automation workflows |

## AI Platform (existing only — not Phase 12 standardized)

| Service | Role |
|---|---|
| Ollama | Model runtime |
| Open WebUI | Chat UI |
| Hermes | Agent |
| Honcho (+ postgres/redis/deriver) | Memory/API |
| Odysseus (+ chromadb/searxng/ntfy) | Research stack |

Phase 13 will redesign this platform; Phase 12 only inventories it.
