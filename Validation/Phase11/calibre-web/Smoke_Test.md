# Phase 11 — Calibre-Web Smoke Test

**Timestamp:** 2026-07-30T10:55:00Z  
**Result:** PASS

| Check | Result |
|-------|--------|
| Container | `running` |
| Config mount | `/mnt/monarch/appdata/calibre-web` → `/config` |
| Books mount | `/hive/library/.../novelas` → `/books` (unchanged) |
| Traefik `https://calib.fatherfankscloud.uk/` | 302 (login — expected) |
| Logs | LSIO init done; listening 8083 |
| Sibling calibre | still running on appdata |
