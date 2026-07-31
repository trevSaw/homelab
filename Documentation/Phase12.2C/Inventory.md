# Phase 12.2C — Radarr Inventory (pre-cutover)

**Captured:** 2026-07-31

| Field | Value |
|---|---|
| Install type | Docker |
| Live compose label | `/var/lib/casaos/apps/radarr/docker-compose.yml` |
| Prior repo import | `services/radarr/compose.yaml` (hotio-only, `/DATA` mounts) |
| Image | `ghcr.io/hotio/radarr:latest` |
| Version | `5.22.4.9896` (master) |
| App data | `/DATA/AppData/radarr/config` (~491M; DB ~18M) |
| Ownership | `fatherfrank:fatherfrank` (1000:1000) |
| Network | `hotio_default` only |
| Port | `7878` |
| Root folder | `/movies/` → host `/hive/jellyfin/movie` |
| Downloads mount | `/hive/downloads` → `/downloads` |
| Movies | 231 |
| Indexers | 6 |
| Quality profiles | 8 |
| Download clients (broken) | NZBGet + qbit → `172.27.0.7` (Radarr self-IP) |
| Remote path mapping | Host `qbittorrent`, remote `/hive/downloads/completed/Radarr/` → local `/downloads/completed/Radarr/` |
| Auth | Forms (`AuthenticationRequired=DisabledForLocalAddresses`) |
