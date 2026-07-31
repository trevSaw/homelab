# Phase 12.2C Known Exceptions

| Exception | Reason | Risk | Mitigation |
|---|---|---|---|
| NZBGet client uses `qbittorrent:6789` not `nzbget:6789` | NZBGet `network_mode: container:qbittorrent` — no distinct DNS name | Low | Documented in media-stack networking; redesign later |
| Host port `7878` still published | Transitional alongside new Traefik router | Low | Remove after `radarr.fatherfankscloud.uk` confirmed in daily use |
| Movie library path `/hive/jellyfin/movie` (not `/hive/media/…`) | Preserve existing root folder `/movies` | Low | Identity mount; path migration separate |
| Downloads `/hive/downloads` (not `/hive/media/downloads`) | Preserve remote path mappings | Low | Same |
| Legacy `/DATA/AppData/radarr` left in place | Rollback / forensics | Low | Not mounted after cutover |
