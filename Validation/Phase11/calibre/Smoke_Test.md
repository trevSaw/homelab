# Phase 11 — Calibre Smoke Test

**Timestamp:** 2026-07-30T10:53:00Z  
**Result:** PASS

| Check | Result |
|-------|--------|
| Container | `running` |
| Config mount | `/mnt/monarch/appdata/calibre` → `/config` |
| Books mount | `/hive/library/Kavita/fanfic/novelas` → `/books` (unchanged) |
| browser_cache | `/hive/library/Kavita/browser_cache` → `/config/browser_cache` (unchanged) |
| Traefik `https://calibre.fatherfankscloud.uk/` | 200 |
| Compose project | `services/calibre-web/compose.yml` |
