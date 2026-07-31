# NZBGet — Smoke Test

**Date:** 2026-07-30  
**Result:** PASS

| Check | Result |
|---|---|
| Container running | Up (`ghcr.io/hotio/nzbget`) |
| Mount `/config` | `/mnt/monarch/appdata/nzbget` |
| Mount `/downloads` | `/hive/downloads` (unchanged) |
| Network | `container:qbittorrent` |
| WebUI `http://127.0.0.1:6789/` | **401** (auth required — endpoint alive) |
| Logs | Clean start: `nzbget 25.2 server-mode`, `using /config/nzbget.conf`, listening `0.0.0.0:6789` |
| Permission / mount errors | None |

## Notes

- Image tag resolved to NZBGet **25.2** (was previously reporting 24.2 in older inspect metadata). Functionally OK; version bump is from `ghcr.io/hotio/nzbget` without a pinned digest.
- Hotio entrypoint ran `Applying permissions to /config` (PUID/PGID 1000) — expected.
