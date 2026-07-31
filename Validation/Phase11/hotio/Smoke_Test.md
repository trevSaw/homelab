# Hotio (qbittorrent) — Smoke Test

**Date:** 2026-07-30  
**Result:** PASS

| Check | Result |
|---|---|
| Container | `qbittorrent` Up |
| Mount `/config` | `/mnt/monarch/appdata/hotio` |
| Mount `/downloads` | `/hive/downloads/completed` |
| WebUI `:8080` | **200** |
| WireGuard init | `init-wireguard successfully started` |
| Privoxy | started |
| NZBGet after recreate | **401** on `:6789` (expected auth) |

## Dependency note

Recreating qbittorrent invalidated NZBGet's `network_mode: container:<old-id>`. NZBGet was recreated via `services/NZBget/compose.yml` and rejoined the new qbittorrent network namespace. Both services healthy afterward.
