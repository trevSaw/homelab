# Bazarr (Phase 12.4)

Subtitle companion. Config: `/mnt/monarch/appdata/bazarr`. Media mounts unchanged under `/hive/jellyfin/{movie,tv}`.

- Networks: `proxy` + `hotio`
- Traefik: `bazarr.fatherfankscloud.uk`
- Sonarr via host LAN (host-net exception); Radarr via Docker DNS `radarr`

```bash
cd services/bazarr
cp .env.example .env
docker compose -f compose.yml up -d
```
