# Prowlarr (Phase 12.2D)

Indexer manager. Migrated from CasaOS `/DATA/AppData/config` to Phase 12 standard.

- Config: `/mnt/monarch/appdata/prowlarr`
- Networks: `proxy` + `hotio` (`hotio_default`)
- WebUI: host `:9696` (transitional) and Traefik `prowlarr.fatherfankscloud.uk`

App integrations:
- Radarr via Docker DNS (`radarr` / `prowlarr`)
- Sonarr via host LAN IP (Sonarr still `network_mode: host` — documented exception)

```bash
cd services/prowlarr
cp .env.example .env
docker compose -f compose.yml up -d
```
