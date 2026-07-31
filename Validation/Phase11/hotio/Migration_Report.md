# Hotio (qbittorrent) — Migration Report

**Date:** 2026-07-30  
**Final decision:** **READY FOR SOAK**

## Summary

Hotio/qBittorrent config (including WireGuard + Privoxy) migrated from `/hive/Hotio/config` to `/mnt/monarch/appdata/hotio`. Downloads remain on `/hive/downloads/completed`. Compose volume for `/config` rewritten only.

| Path | Location |
|---|---|
| New config | `/mnt/monarch/appdata/hotio` (~23 MB live) |
| Rollback | `/hive/Hotio/config.old` (21 MB) |
| Downloads | `/hive/downloads/completed` |
| Compose | `services/Hotio/compose.yml` |

## Execution

| Step | Result |
|---|---|
| Dry-run | SUCCESS (~22 MB / 854 files) |
| Review | APPROVED |
| Stop / copy / checksum | SUCCESS — checksum inventory matches |
| Apply compose | SUCCESS |
| Start | SUCCESS — VPN + Privoxy + WebUI |
| Smoke | PASS (`:8080` → 200) |
| Rename → `.old` | SUCCESS |
| NZBGet recovery | Recreated after qbittorrent ID change — PASS |

## Compose diff

```diff
-        source: /hive/Hotio/config
+        source: /mnt/monarch/appdata/hotio
```

## Rollback

```bash
cd /home/fatherfrank/projects/homelab/services/Hotio
docker compose stop
mv /hive/Hotio/config.old /hive/Hotio/config
# restore compose volume to /hive/Hotio/config (or use pre-migrate.bak)
docker compose up -d
# then recreate NZBGet so it rejoins qbittorrent network:
cd ../NZBget && docker compose up -d --force-recreate
```

Keep `.old` ≥ **7 days**.

## Lessons learned

1. Any recreate of qbittorrent breaks NZBGet's `network_mode: container:<id>` — always recreate NZBGet afterward.
2. VPN stack (WireGuard) came up cleanly from the copied config; no special ownership remapping needed (PUID 1000).
