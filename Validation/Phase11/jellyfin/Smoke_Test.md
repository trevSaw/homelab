# Jellyfin — Smoke Test

**Date:** 2026-07-31  
**Context:** Post-cutover on `/mnt/monarch/appdata/jellyfin`

| Check | Result |
|---|---|
| `docker compose up -d` | SUCCESS (recreated from repo compose) |
| Container status | running |
| Docker healthcheck | **healthy** |
| `curl http://127.0.0.1:8096/health` | Healthy / HTTP 200 |
| Config mount | `/mnt/monarch/appdata/jellyfin` → `/config` |
| Media mounts | `/hive/jellyfin/tv`, `/hive/jellyfin/movie` unchanged |
| Users | `fatherfrank`, `test` |
| UserData rows | 19,809 |
| Playback Reporting activities | 444 |
| Metadata files | 24,573 |
| Plugins loaded | 7 plugin dirs present |
| Library roots | Anime, Cartoons, Collections, Drama, Fantasy, KDramas, Movies, … |
| `/System/Info/Public` | 10.11.6, wizard completed |
| Error-like log lines (5m) | none |

Framework smoke: `reports/smoke-jellyfin.txt` → `smoke_complete`.
