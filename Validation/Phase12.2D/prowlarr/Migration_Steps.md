# Migration steps — Phase 12.2D Prowlarr

1. Inventory CasaOS Prowlarr (`hotio_default`, `/DATA/AppData/config`, 10 indexers)
2. Stop; WAL checkpoint; backup → `/hive/backups/prowlarr/pre-12.2D-*`
3. Rsync → `/mnt/monarch/appdata/prowlarr`
4. Fix Applications: Radarr → Docker DNS; Sonarr → keep host LAN (exception)
5. Deploy dual-homed `compose.yml` + Traefik from `services/prowlarr`
6. Validate health, indexers, app tests, sync commands
