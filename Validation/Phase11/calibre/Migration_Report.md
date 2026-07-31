# Phase 11 — Calibre Migration Report

**Service:** calibre  
**Batch:** 02  
**Final status:** READY FOR SOAK  
**Completed:** 2026-07-30T10:53:30Z

## Summary

Calibre config migrated `/hive/calibre/config` → `/mnt/monarch/appdata/calibre`. Books remain on `/hive/library`. Compose volume for calibre only updated in shared `services/calibre-web/compose.yml`.

## Paths

| Role | Path |
|------|------|
| Rollback | `/hive/calibre/config.old` |
| Destination | `/mnt/monarch/appdata/calibre` |
| Compose backup | `Validation/Phase11/calibre/proposed/calibre/compose.yml.pre-migrate.bak` |

## Compose change

```diff
-      - /hive/calibre/config:/config
+      - /mnt/monarch/appdata/calibre:/config
```

Books + browser_cache binds unchanged.

## Issues

- User rsync hit 2 mode-`000` Qt shader cache files → exit 23. Completed via docker-root rsync; checksum **MATCH** (312 files).

## Rollback

```bash
cp -a Validation/Phase11/calibre/proposed/calibre/compose.yml.pre-migrate.bak \
  services/calibre-web/compose.yml
mv /hive/calibre/config.old /hive/calibre/config
(cd services/calibre-web && docker compose -f compose.yml up -d calibre)
```

## Final decision

**READY FOR SOAK** — leave `.old` ≥ 7 days.
