# Migration steps — Phase 12.2C Radarr

1. Inventory live CasaOS/Docker Radarr (`hotio_default`, `/DATA/...`, broken client IPs)
2. Stop container; WAL checkpoint; backup → `/hive/backups/radarr/pre-12.2C-*`
3. Rsync state → `/mnt/monarch/appdata/radarr`
4. Update DownloadClients Settings host → `qbittorrent` (ports 8080 / 6789)
5. Replace compose with Phase 12 dual-homed `compose.yml` + env/Versions/README
6. `docker compose up -d` from `services/radarr`
7. Validate health, 231 movies, client tests PASS, networks `proxy`+`hotio`
