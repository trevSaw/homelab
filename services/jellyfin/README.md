# Jellyfin (Phase 12.4)

Media server. Config: `/mnt/monarch/appdata/jellyfin`. Libraries remain on `/hive/jellyfin/{tv,movie}`.

- Network: `proxy` only
- Traefik: `jellyfin.fatherfankscloud.uk`
- Host `:8096` transitional
- HW accel: `/dev/dri` (+ NVIDIA env retained)

```bash
cd services/jellyfin
cp .env.example .env
docker compose -f compose.yml up -d
```
