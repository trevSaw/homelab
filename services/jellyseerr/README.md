# Jellyseerr (Phase 12.4)

Request UI (Overseerr-compatible). Config: `/mnt/monarch/appdata/jellyseerr`.

- Network: `proxy` only (canonical Overseerr role)
- Traefik: `jellyseerr.fatherfankscloud.uk`
- Host `:5055` transitional
- Integrations: Jellyfin/`jellyfin`, Radarr/`radarr` (Docker DNS on `proxy`); Sonarr via host LAN (Sonarr still host-networked)

```bash
cd services/jellyseerr
cp .env.example .env
docker compose -f compose.yml up -d
```
