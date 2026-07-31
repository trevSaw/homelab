# Service Inventory — Phase 12 Closeout

**Snapshot:** 2026-07-31 · 42 running containers  

Legend — **SoT**: `repo` = `services/` compose; `appdata` = compose under `/mnt/monarch/appdata`; `hive`/`casaos` = not Phase-12 SoT.

## Phase 12 standardized (primary)

| Service | Compose | Image / pin | Health | Appdata | Networks | Traefik | Notes / exceptions |
|---|---|---|---|---|---|---|---|
| Traefik | `services/traefik` | `traefik:v3.6.7` | healthy | ACME file | `proxy` | dashboard | Host 80/443 |
| Portainer | `services/portainer` | `portainer-ce:2.33.6` | none* | yes | `portainer_network` | no | Distroless health exemption |
| Beszel | `services/beszel` | `0.18.7` | none | yes | `homelab` | no | Phase 12.1 |
| Beszel-agent | `services/beszel_agent` | `0.18.7` | none | yes | `host` | no | Host net exception |
| Uptime Kuma | `services/uptime-kuma` | `1.23.10-alpine` | healthy | yes | `proxy` | no | Host :3001 |
| qBittorrent | `services/Hotio` | `qbittorrent:release-4.5.5` | healthy | `…/hotio` | `hotio_default` | no | VPN / NET_ADMIN |
| NZBGet | `services/NZBget` | digest pin 25.2 | healthy | `…/nzbget` | container:qbittorrent | no | Shared VPN netns |
| Sonarr | `services/sonarr` | `sonarr:version-3.0.10.1566` | healthy | `…/sonarr` | **host** | no | Host-net debt |
| Radarr | `services/radarr` | `radarr:release-5.22.4.9896` | healthy | `…/radarr` | proxy+hotio | yes | Port 7878 transitional |
| Prowlarr | `services/prowlarr` | `prowlarr:release-2.3.5.5327` | healthy | `…/prowlarr` | proxy+hotio | yes | Port 9696 transitional |
| Jellyfin | `services/jellyfin` | `jellyfin:release-10.11.6` | healthy | `…/jellyfin` | proxy | yes | :8096 transitional; `/dev/dri` |
| Jellyseerr | `services/jellyseerr` | digest 2.7.3 | healthy | `…/jellyseerr` | proxy | yes | :5055 transitional |
| Bazarr | `services/bazarr` | `bazarr:1.2.2` | healthy | `…/bazarr` | proxy+hotio | yes | :6767 transitional |

\*Portainer probed externally in 12.1.

## Identity / portal (repo or hybrid)

| Service | Compose | Image | Networks | Traefik |
|---|---|---|---|---|
| Authentik server/worker/db/redis | `services/authentic` | `2024.12.3` / postgres/redis | authentik + proxy | server yes |
| Homepage | `services/homepage` | `homepage:latest` | proxy | yes |
| Calibre / Calibre-web | `services/calibre-web` | linuxserver `:latest` | proxy | yes |
| code-server | `services/code-server` | `:latest` | proxy + ollama net | yes |

## Not Phase-12 standardized (still production)

| Service | Compose hint | Notes |
|---|---|---|
| Nextcloud + db | `/hive/cloud` | Traefik on proxy |
| Kavita | `/hive/library/Kavita` | Traefik |
| Readarr | `/data/compose/39` | hotio; develop tag |
| Byparr | `/data/compose/50` | hotio |
| Actual | CasaOS | — |
| Crafty | CasaOS | many game ports |
| LazyLibrarian | CasaOS | — |
| MariaDB | CasaOS | — |
| n8n | appdata compose | homelab + ai-assistant |
| Ollama / Open WebUI | `/hive/ollama` | AI |
| Hermes / Honcho* | appdata compose | AI |
| Odysseus stack | appdata compose | AI |

Full machine-readable table: `Validation/Phase12.5/Docker_Inventory.md`.
