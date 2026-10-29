# Seerr (Phase 12.4) — formerly Jellyseerr

Request UI (Overseerr-compatible). Config: `/mnt/monarch/appdata/jellyseerr`.

- Image: `ghcr.io/hotio/seerr:release-3.4.1` (upgraded from jellyseerr 2.7.3; fixes Jellyfin 12 legacy-auth incompatibility)
- Network: `proxy` only (canonical Overseerr role)
- Traefik: `jellyseerr.fatherfankscloud.uk`
- Host `:5055` transitional
- Integrations: Jellyfin/`jellyfin`, Radarr/`radarr` (Docker DNS on `proxy`); Sonarr via host LAN (Sonarr still host-networked)

Pre-upgrade backup: `/hive/backups/jellyseerr/pre-3.4.1-<timestamp>/`.

```bash
cd services/jellyseerr
cp .env.example .env
docker compose -f compose.yml up -d
```
