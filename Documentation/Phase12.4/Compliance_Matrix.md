# Phase 12.4 — Compliance Matrix

| Service | Repo SoT | Appdata | Networks | Traefik | Status |
|---|---|---|---|---|---|
| Jellyfin | yes | `/mnt/monarch/appdata/jellyfin` | `proxy` | yes | **PASS (Documented Exception)** — transitional `:8096` |
| Jellyseerr | yes | `/mnt/monarch/appdata/jellyseerr` | `proxy` | yes | **PASS (Documented Exception)** — transitional `:5055`; Sonarr via LAN |
| Bazarr | yes | `/mnt/monarch/appdata/bazarr` | `proxy`+`hotio` | yes | **PASS (Documented Exception)** — transitional `:6767`; Sonarr via LAN |
| Lidarr | — | — | — | — | **N/A** — not deployed |

## Approved exceptions

| Exception | Why |
|---|---|
| Host ports 8096 / 5055 / 6767 | Transitional beside Traefik |
| Sonarr integrations via `192.168.50.44` | Sonarr still host-networked |
| Jellyfin `/dev/dri` + NVIDIA env | Hardware transcoding |
| Legacy `/hive/jellyfin/...` paths | Preserve libraries; `/hive/media` later |
| Hotio image digest for Jellyseerr | No reliable `release-2.7.3` tag on registry probe |
