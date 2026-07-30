# Phase 10.75 — Service Inventory

Live inventory captured 2026-07-30. Paths under `/DATA/AppData` resolve via CasaOS data root (typically `/hive/AppData`).

## CasaOS-managed (running) — imported

| Container | Image | Compose (live) | Config / data binds | Ports | Networks |
|---|---|---|---|---|---|
| prowlarr | `ghcr.io/hotio/prowlarr:latest` | `/var/lib/casaos/apps/glorious_thomas/docker-compose.yml` | `/DATA/AppData/config` → `/config` | 9696 | `hotio_default` |
| radarr | `ghcr.io/hotio/radarr:latest` | `/var/lib/casaos/apps/radarr/docker-compose.yml` | config + `/hive/jellyfin/movie` + `/hive/downloads` | 7878 | `hotio_default` |
| jellyseerr | `ghcr.io/hotio/jellyseerr:latest` | `/var/lib/casaos/apps/breathtaking_ken/docker-compose.yml` | `/DATA/AppData/jellyseerr/config` | 5055 | `jellyfin_default`, `hotio_default` |
| bazarr | `linuxserver/bazarr:1.2.2` | `/var/lib/casaos/apps/bazarr/docker-compose.yml` | config + movie + tv | 6767 | `hotio_default` |
| actual-server | `actualbudget/actual-server:25.10.0` | `/var/lib/casaos/apps/big-bear-actual-server/docker-compose.yml` | `/DATA/AppData/big-bear-actual-server` → `/data` | 5006 | `big-bear-actual-server_default` |
| linuxserver-lazylibrarian-app-1 | `linuxserver/lazylibrarian:version-3682faed` | `/var/lib/casaos/apps/linuxserver-lazylibrarian/docker-compose.yml` | config/downloads/books under `/DATA/AppData/lazylibrarian` | 5299 | project default |
| big-bear-crafty | `registry.gitlab.com/crafty-controller/crafty-4:latest` | `/var/lib/casaos/apps/big-bear-crafty/docker-compose.yml` | five binds under `/DATA/AppData/big-bear-crafty/data` | 8443,8123,19132/udp,25500–25600 | `big-bear-crafty` |
| linuxserver-mariadb-app-1 | `linuxserver/mariadb:latest` | `/var/lib/casaos/apps/linuxserver-mariadb/docker-compose.yml` | `/DATA/AppData/mariadb/config` | 3308→3306 | project default |
| uptimekuma | `louislam/uptime-kuma:1.23.10-alpine` | `/var/lib/casaos/apps/uptimekuma/docker-compose.yml` | `/DATA/AppData/uptimekuma/app/data` | 3001 | `bridge` |

## Portainer-managed (running) — imported

| Container | Image | Compose (live) | Binds | Ports | Networks |
|---|---|---|---|---|---|
| byparr-byparr-1 | `ghcr.io/thephaseless/byparr:latest` | `/data/compose/50/docker-compose.yml` | none | 8191 unpublished | `hotio_default` |
| readarr | `lscr.io/linuxserver/readarr:develop` | `/data/compose/39/docker-compose.yml` | `/hive/readarr`, books, downloads | 8787 | `hotio_default` |

## Hive-managed (running, not previously in `services/`) — imported

| Container | Image | Compose (live) | Notes |
|---|---|---|---|
| kavita | `jvmilazz0/kavita:latest` | `/hive/library/Kavita/compose.yml` | Config on `/ssd/appdata/kavita/config`; media on `/hive/library/Kavita/*` |
| nextcloud / nextcloud-db | `nextcloud:31` / `mariadb:10.11` | `/hive/cloud/compose.yaml` | DB already on `/mnt/monarch/databases/nextcloud-mariadb` |

## Already repository-present (not re-imported)

Examples: `traefik`, `portainer`, `homepage`, `authentik`, `n8n`, `ollama`/`open-webui`, `honcho`, `hermes`, `beszel`, `jellyfin`, `NZBget`, `Hotio`, `calibre-web`, `code-server`, `odysseus`, …

## Restart policy

All imported services use `restart: unless-stopped` (confirmed via inspect).
