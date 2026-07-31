# Jellyfin — Dry Run Review (updated for successful cutover)

**Date:** 2026-07-31  
**Decision:** **APPROVED** → executed → **READY FOR SOAK**

## Final policy

| Item | Value |
|---|---|
| Source | `/hive/jellyfin/config` |
| Destination | `/mnt/monarch/appdata/jellyfin` |
| Excludes | `cache/**`, `data/transcodes/**`, `.temp/**`, `log/**` |
| Keep on hive | `/hive/jellyfin/tv`, `/hive/jellyfin/movie` |
| Migratable size | **~7.0 GB** / 41,099 files |
| Compose change | config volume only |

Must-keep retained: `data/data`, `data/metadata`, `data/plugins`, `data/root`, `dlna`, `.aspnet`, XML configs, all `*.db*`.

See [Migration_Report.md](Migration_Report.md) for the completed cutover.
