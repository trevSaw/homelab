# Phase 12.4 — Known Exceptions

| Service | Exception | Mitigation |
|---|---|---|
| Jellyfin | Host `:8096` | Prefer Traefik; remove after client soak |
| Jellyfin | `/dev/dri` device | Required for HW transcode |
| Jellyseerr | Host `:5055` | Prefer Traefik hostname |
| Jellyseerr / Bazarr | Sonarr via LAN IP | Until Sonarr dual-home |
| Bazarr | Host `:6767` | Prefer Traefik |
| All | Media under `/hive/jellyfin/...` not `/hive/media` | Future path migration |
