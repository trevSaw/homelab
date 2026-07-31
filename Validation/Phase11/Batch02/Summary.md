# Phase 11 — Batch 02 Summary

**Batch:** 02  
**Executed:** 2026-07-30  
**Overall status:** READY FOR 7-DAY SOAK  
**Next batch:** Do not proceed until soak criteria are met (unless operator overrides)

## Services migrated (order)

| # | Service | Final status | New path | Rollback `.old` |
|---|---------|--------------|----------|-----------------|
| 1 | Authentik | READY FOR SOAK | `/mnt/monarch/appdata/authentik` | `/hive/data/authentik.old`, `/hive/authentic.old` |
| 2 | Calibre | READY FOR SOAK | `/mnt/monarch/appdata/calibre` | `/hive/calibre/config.old` |
| 3 | Calibre-Web | READY FOR SOAK | `/mnt/monarch/appdata/calibre-web` | `/hive/calibre-web/config.old` |

## Issues & resolutions

1. **Authentik** initially `verify|partial` with empty source — remapped `services.conf` to `/hive/data/authentik`.  
2. **Postgres uid 70** — docker-root rsync required (user rsync would break ownership).  
3. **Authentik healthcheck** used missing `wget` → Traefik filtered unhealthy server → SSO 404; fixed to Python urllib probe.  
4. **Calibre** two mode-`000` Qt shader cache files blocked user rsync — completed via docker-root; checksum match.  
5. Books/library paths never moved (policy preserved).

## Outstanding warnings

- Authentik/Portainer-style healthcheck lessons: ensure probes work in image or Traefik will hide the route.  
- Gitignored `services/.env` holds Authentik secrets — do not commit.  
- Homepage images `.old` rename from Batch 01 still needs sudo if not done.

## Rollback summary

Per-service backups under `Validation/Phase11/<service>/proposed/` and hive `*.old` trees. Framework: `./scripts/migration/rollback.sh --execute --phase-dir Validation/Phase11/<service> <key>` (Authentik may need manual PATH_DATA + root data restore).

## Recommended next services

After soak: higher/final wave (ollama, jellyfin, nzbget, hotio) with explicit windows — especially NZBget excludes and ollama model size.

## Operator summary

- **Succeeded:** Authentik, Calibre, Calibre-Web  
- **Failed:** none (after remediations)  
- **Ready for 7-day soak?** **Yes**  
- **Phase 11 Batch 03?** **Do not proceed yet**
