# Storage Architecture — Phase 12 Closeout

## Principles

| Class | Location | Rule |
|---|---|---|
| Application state | `/mnt/monarch/appdata/<service>` | Config, DB, metadata |
| Bulk media | `/hive/...` | Never in appdata |
| Downloads | `/hive/downloads` (live) | Target doc: `/hive/media/downloads` |
| Phase 12 cutover backups | `/hive/backups/<service>/` | Pre-migration snapshots |

## Live layout (production)

### Monarch appdata (`/mnt/monarch/appdata`)

Present at closeout (non-exhaustive): `authentik`, `bazarr`, `beszel`, `beszel_agent`, `calibre`, `calibre-web`, `code-server`, `hermes`, `homepage`, `honcho`, `hotio`, `jellyfin`, `jellyseerr`, `kavita`, `n8n`, `nzbget`, `odysseus`, `open-webui`, `portainer`, `prowlarr`, `radarr`, `sonarr`, `traefik`, `uptime-kuma`, …

### Hive media / downloads (live paths)

| Path | Used by |
|---|---|
| `/hive/jellyfin/tv` | Jellyfin, Sonarr, Bazarr |
| `/hive/jellyfin/movie` | Jellyfin, Radarr, Bazarr |
| `/hive/downloads` | Sonarr, Radarr, NZBGet |
| `/hive/downloads/completed` | qBittorrent (+ categories) |

Canonical **target** (not fully migrated): `/hive/media/` and `/hive/media/downloads`.

### Backups captured in Phase 12

| Service | Location (approx size) |
|---|---|
| Sonarr | `/hive/backups/sonarr/` (~312M) |
| Radarr | `/hive/backups/radarr/` (~431M) |
| Prowlarr | `/hive/backups/prowlarr/` (~16M) |
| Jellyseerr | `/hive/backups/jellyseerr/` (~1.2M) |
| Bazarr | `/hive/backups/bazarr/` (~13M) |

## Diagram

```text
/mnt/monarch/appdata/<svc>  ──►  container /config
/hive/jellyfin/{tv,movie}   ──►  libraries
/hive/downloads[/*]         ──►  download clients / *arr
/hive/backups/<svc>         ──►  Phase 12 migration rollbacks
```
