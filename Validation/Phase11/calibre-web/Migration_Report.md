# Phase 11 — Calibre-Web Migration Report

**Service:** calibre-web  
**Batch:** 02  
**Final status:** READY FOR SOAK  
**Completed:** 2026-07-30T10:55:30Z

## Summary

Calibre-Web config migrated `/hive/calibre-web/config` → `/mnt/monarch/appdata/calibre-web`. Books stay on `/hive/library`. Shared compose updated for calibre-web path only (calibre already on appdata).

## Paths

| Role | Path |
|------|------|
| Rollback | `/hive/calibre-web/config.old` |
| Destination | `/mnt/monarch/appdata/calibre-web` |
| Compose backup | `Validation/Phase11/calibre-web/proposed/calibre-web/compose.yml.pre-migrate.bak` |
| Hive compose stash | `/hive/calibre-web.compose.old/` (legacy compose files) |

## Compose change

```diff
-      - /hive/calibre-web/config:/config
+      - /mnt/monarch/appdata/calibre-web:/config
```

## Verification

Checksum match while stopped (6 files / 1 dir, ~335KB).

## Final decision

**READY FOR SOAK** — leave `.old` ≥ 7 days.
