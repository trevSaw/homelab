# Sonarr (Phase 21)

TV series manager.

- Config: `/mnt/monarch/appdata/sonarr`
- TV libraries: `/hive/jellyfin/tv` (unchanged)
- Downloads: `/hive/downloads` (unchanged)
- Image: `lscr.io/linuxserver/sonarr:version-4.0.19.2979` (upgraded from v3)
- Networks: `proxy` + `hotio_default` (moved off `host` network)
- Traefik: `sonarr.fatherfankscloud.uk`
- Host `:8989` transitional
- Download clients: `qbittorrent` host (NZBGet shares qBittorrent netns), matching Radarr

```bash
cd services/sonarr
cp .env.example .env   # if needed
docker compose up -d
```

Do not use `/hive/Hotio/sonarr` (abandoned).