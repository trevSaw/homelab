# Phase 12.2B — Native Sonarr Inventory

**Captured:** 2026-07-31  
**Host:** mocha

## Runtime (before cutover)

| Item | Value |
|---|---|
| Unit | `sonarr.service` (`/lib/systemd/system/sonarr.service`) |
| Exec | `/usr/bin/mono --debug /usr/lib/sonarr/bin/Sonarr.exe -nobrowser -data=/var/lib/sonarr` |
| User/Group | `fatherfrank:fatherfrank` (UID/GID 1000) |
| UMask | `0002` |
| Package | `sonarr` `3.0.10` |
| Release | `3.0.10.1566` |
| Branch | `main` |
| Port | `8989` |
| Auth | `None` (config.xml) |
| Data | `/var/lib/sonarr` (~377M; DB ~66M) |
| Series | **214** |
| Indexers | 8 |
| Quality profiles | 10 |
| Download clients | NZBGet `localhost:6789`, qBittorrent `localhost:8080` |

## Root folders (host paths)

- `/hive/jellyfin/tv/Drama_Series/`
- `/hive/jellyfin/tv/Fantasy_Series/`
- `/hive/jellyfin/tv/Kdrama_Series/`
- `/hive/jellyfin/tv/Anime_Series/`
- `/hive/jellyfin/tv/Cartoons/`
- `/hive/jellyfin/tv/JDrama/`
- `/hive/jellyfin/tv/Reality/`
- `/hive/jellyfin/tv/`

## Remote path mappings

| Host | Remote | Local |
|---|---|---|
| localhost | `/downloads/completed/Sonarr/` | `/hive/downloads/completed/Sonarr/` |
| localhost | `/downloads/completed/Sonarr` | `/hive/downloads/completed/Sonarr/` |

## Abandoned path (not source)

`/hive/Hotio/sonarr` — old Docker remnant (15 series, develop). Excluded from migration.
