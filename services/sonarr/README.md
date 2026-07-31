# Sonarr (Phase 12.2B)

Migrated from native systemd/mono (`/var/lib/sonarr`) to Docker.

- Config: `/mnt/monarch/appdata/sonarr`
- TV libraries: `/hive/jellyfin/tv` (unchanged)
- Downloads: `/hive/downloads` (unchanged)
- WebUI: `http://mocha:8989` (host network)

```bash
cd services/sonarr
cp .env.example .env   # if needed
docker compose up -d
```

Do not use `/hive/Hotio/sonarr` (abandoned).
