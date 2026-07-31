# Container Inventory — Media Network Audit

**Date:** 2026-07-31  
**Method:** `docker inspect` / `docker network inspect` (read-only)  
**Running containers on host:** 42 (all running at audit time)

Canonical media services and closely related containers are listed below. Non-media containers on `proxy` (Authentik, Nextcloud, etc.) are omitted except Traefik.

---

## Traefik

| Field | Value |
|---|---|
| Container | `traefik` |
| Compose project | `traefik` |
| Compose file | `services/traefik/compose.yaml` |
| Image | `traefik:v3.6.7` |
| Networks | `proxy` |
| network_mode | `proxy` |
| Published ports | `80`, `443` |
| Traefik labels | Dashboard router `Host(traefik.fatherfankscloud.uk)` |
| Volumes | ACME `…/traefik/acme.json`, docker.sock, localtime |
| Health | healthy |

---

## Jellyfin

| Field | Value |
|---|---|
| Container | `jellyfin` |
| Compose project | `jellyfin` |
| Compose file | `services/jellyfin/compose.yml` |
| Image | `ghcr.io/hotio/jellyfin:latest` |
| Networks | `proxy` |
| network_mode | `proxy` |
| Published ports | `8096` |
| Traefik labels | `enable=true`, `Host(jellyfin.fatherfankscloud.uk)`, tls/le, LB port `8096` |
| Volumes | `/mnt/monarch/appdata/jellyfin` → `/config`; `/hive/jellyfin/tv` → `/data/tvshows`; `/hive/jellyfin/movie` → `/data/movies` |
| Health | healthy |

---

## Sonarr

| Field | Value |
|---|---|
| Container | `sonarr` |
| Compose project | `sonarr` |
| Compose file | `services/sonarr/compose.yml` |
| Image | `lscr.io/linuxserver/sonarr:version-3.0.10.1566` |
| Networks | `host` |
| network_mode | `host` |
| Published ports | (host mode; listens `:8989` on host) |
| Traefik labels | none |
| Volumes | `/mnt/monarch/appdata/sonarr` → `/config`; identity mounts `/hive/jellyfin/tv`, `/hive/downloads` |
| Health | healthy |
| App notes | Download clients: NZBGet/`localhost:6789`, qBittorrent/`localhost:8080` |

---

## Radarr

| Field | Value |
|---|---|
| Container | `radarr` |
| Compose project | `radarr` |
| Compose file | `/var/lib/casaos/apps/radarr/docker-compose.yml` |
| Image | `ghcr.io/hotio/radarr:latest` |
| Networks | `hotio_default` (`172.27.0.7`) |
| network_mode | `hotio_default` |
| Published ports | `7878` |
| Traefik labels | none |
| Volumes | `/DATA/AppData/radarr/config` → `/config`; `/hive/jellyfin/movie` → `/movies`; `/hive/downloads` → `/downloads` |
| Health | none |
| App notes | Download clients both host=`172.27.0.7` (self) ports `6789`/`8080` — **incorrect** vs qBittorrent `172.27.0.4` |

---

## Prowlarr

| Field | Value |
|---|---|
| Container | `prowlarr` |
| Compose project | `glorious_thomas` (CasaOS) |
| Compose file | `/var/lib/casaos/apps/glorious_thomas/docker-compose.yml` |
| Image | `ghcr.io/hotio/prowlarr:latest` |
| Networks | `hotio_default` (`172.27.0.6`) |
| network_mode | `hotio_default` |
| Published ports | `9696` |
| Traefik labels | none |
| Volumes | `/DATA/AppData/config` → `/config` |
| Health | none |

---

## Bazarr (deployed)

| Field | Value |
|---|---|
| Container | `bazarr` |
| Compose project | `bazarr` |
| Compose file | `/var/lib/casaos/apps/bazarr/docker-compose.yml` |
| Image | `linuxserver/bazarr:1.2.2` |
| Networks | `hotio_default` (`172.27.0.2`) |
| network_mode | `bridge` (attached to `hotio_default`) |
| Published ports | `6767` |
| Traefik labels | none |
| Volumes | `/DATA/AppData/bazarr/config`; `/hive/jellyfin/movie` → `/movies`; `/hive/jellyfin/tv` → `/tv` |
| Health | none |

---

## Lidarr

**Not deployed** (no container).

---

## Overseerr / Jellyseerr

Overseerr brand not present. **Jellyseerr** fulfills the request-UI role:

| Field | Value |
|---|---|
| Container | `jellyseerr` |
| Compose project | `breathtaking_ken` (CasaOS) |
| Compose file | `/var/lib/casaos/apps/breathtaking_ken/docker-compose.yml` |
| Image | `ghcr.io/hotio/jellyseerr:latest` |
| Networks | `hotio_default` (`172.27.0.3`), `jellyfin_default` (`172.18.0.2`) |
| network_mode | `bridge` |
| Published ports | `5055` |
| Traefik labels | none |
| Volumes | `/DATA/AppData/jellyseerr/config` → `/config` |
| Health | none |

---

## qBittorrent (Hotio)

| Field | Value |
|---|---|
| Container | `qbittorrent` |
| Compose project | `hotio` |
| Compose file | `services/Hotio/compose.yml` |
| Image | `ghcr.io/hotio/qbittorrent:release-4.5.5` |
| Networks | `hotio_default` (`172.27.0.4`) |
| network_mode | `hotio_default` |
| Published ports | `8080`, `8118`, `6789` |
| Traefik labels | none |
| Volumes | `/mnt/monarch/appdata/hotio` → `/config`; `/hive/downloads/completed` → `/downloads` |
| Health | healthy |

---

## NZBGet

| Field | Value |
|---|---|
| Container | `nzbget` |
| Compose project | `nzbget` |
| Compose file | `services/NZBget/compose.yml` |
| Image | `ghcr.io/hotio/nzbget@sha256:6815d7e…` |
| Networks | _(none of its own)_ |
| network_mode | `container:<qbittorrent-id>` |
| Published ports | none (uses qBittorrent publishes, including `6789`) |
| Traefik labels | none |
| Volumes | `/mnt/monarch/appdata/nzbget` → `/config`; `/hive/downloads` → `/downloads` |
| Health | healthy |
| DNS note | No distinct `nzbget` name on `hotio`; peers must use `qbittorrent:6789` or host `:6789` |

---

## Related (not in canonical membership table)

### Readarr

- Networks: `hotio_default` (`172.27.0.8`)
- Ports: `8787`
- Config on `/hive/readarr` (not appdata)
- Traefik: none

### Byparr

- Networks: `hotio_default` (`172.27.0.5`)
- Ports: none
- Health: healthy
- Traefik: none

---

## Live network membership snapshot

**proxy:** authentik-server, authentik-worker, calibre, calibre-web, code-server, hermes, homepage, honcho-api, **jellyfin**, kavita, nextcloud, open-webui, **traefik**, uptimekuma  

**hotio_default:** **bazarr**, byparr-byparr-1, **jellyseerr**, **prowlarr**, **qbittorrent**, **radarr**, readarr  

**Not on either (media):** **sonarr** (host), **nzbget** (shared netns with qbittorrent)
