# Validation Summary — Sonarr Phase 12.2B

**Result:** PASS (with one pre-existing root-folder gap)

## Before → After

| Item | Before | After |
|---|---|---|
| Runtime | systemd + mono | Docker linuxserver |
| Data | `/var/lib/sonarr` | `/mnt/monarch/appdata/sonarr` |
| Version | 3.0.10.1566 | 3.0.10.1566 |
| Series | 214 | 214 |
| WebUI | `:8989` | `:8989` (host net) |

## Artifacts

- `01_before.txt`
- `02_backup_info.txt`
- `03_image_pull.txt`
- `04_rsync_to_appdata.txt`
- `05_appdata_verify.txt`
- `06_compose_config.yml`
- `07_compose_up.txt`
- `08_after_inspect.txt`
- `09_validation.txt`
- `Rollback.md`

## Notes

- NZBGet + qBittorrent download-client tests: PASS
- `/hive/jellyfin/tv/JDrama` missing on host (accessible=False) — existed before migration; not changed here
- Source `/hive/Hotio/sonarr` unused (15-series abandoned instance)
