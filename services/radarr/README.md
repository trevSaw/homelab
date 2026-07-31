# Radarr (Phase 12.2C)

Movie manager. Migrated from CasaOS/`/DATA/AppData/radarr` to Phase 12 standard.

- Config: `/mnt/monarch/appdata/radarr`
- Movies: `/hive/jellyfin/movie` → `/movies`
- Downloads: `/hive/downloads` → `/downloads`
- Networks: `proxy` + `hotio` (`hotio_default`)
- WebUI: host `:7878` (transitional) and Traefik `radarr.fatherfankscloud.uk`

Download clients use Docker DNS `qbittorrent` (NZBGet shares qBittorrent netns → `qbittorrent:6789`).

```bash
cd services/radarr
cp .env.example .env
docker compose -f compose.yml up -d
```
