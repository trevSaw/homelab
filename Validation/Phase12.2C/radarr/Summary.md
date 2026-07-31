# Validation Summary — Radarr Phase 12.2C

**Result:** PASS

| Item | Before | After |
|---|---|---|
| Data | `/DATA/AppData/radarr/config` | `/mnt/monarch/appdata/radarr` |
| Networks | `hotio_default` | `proxy` + `hotio_default` |
| Clients | `172.27.0.7` (FAIL) | `qbittorrent` DNS (PASS) |
| Movies | 231 | 231 |
| Version | 5.22.4.9896 | 5.22.4.9896 |

## Artifacts

`01_before.txt` … `09_validation.txt`, `Rollback.md`
