# nextcloud — Phase 10.75 Import Report

**Type:** Repository import only (no storage migration)

## Summary
Imported live service `nextcloud,nextcloud-db` into `services/nextcloud/compose.yaml`.

| Item | Value |
|---|---|
| Former compose | nextcloud (stale); live uses /hive/cloud |
| Source config (future migrate) | `/hive/cloud/nextcloud` |
| Target config (future migrate) | `/mnt/monarch/appdata/nextcloud` |
| Bind mounts changed? | **No** |
| Container recreated? | **No** |

## Files added
- `services/nextcloud/compose.yaml`
- `services/nextcloud/.env.example`
- `services/nextcloud/README.md`
- `Documentation/services/nextcloud/`
