# Phase 10.75 — Import Report

**Date:** 2026-07-30  
**Commit/tag:** annotated tag `phase10.75-casaos-retired` on branch `phase10.5` (local only; not pushed)

## Imported services (13)

| Service dir | Live container(s) | Former orchestrator | Storage migrated? | Recreated? |
|---|---|---|---|---|
| `prowlarr` | `prowlarr` | CasaOS `glorious_thomas` | No | No |
| `radarr` | `radarr` | CasaOS `radarr` | No | No |
| `jellyseerr` | `jellyseerr` | CasaOS `breathtaking_ken` | No | No |
| `bazarr` | `bazarr` | CasaOS `bazarr` | No | No |
| `actual` | `actual-server` | CasaOS `big-bear-actual-server` | No | No |
| `lazylibrarian` | `linuxserver-lazylibrarian-app-1` | CasaOS `linuxserver-lazylibrarian` | No | No |
| `crafty` | `big-bear-crafty` | CasaOS `big-bear-crafty` | No | No |
| `mariadb` | `linuxserver-mariadb-app-1` | CasaOS `linuxserver-mariadb` | No | No |
| `uptime-kuma` | `uptimekuma` | CasaOS `uptimekuma` | No | No |
| `byparr` | `byparr-byparr-1` | Portainer `/data/compose/50` | No | No |
| `readarr` | `readarr` | Portainer `/data/compose/39` | No | No |
| `kavita` | `kavita` | Hive `/hive/library/Kavita` | No | No |
| `nextcloud` | `nextcloud`, `nextcloud-db` | Hive `/hive/cloud` | No | No |

## What each import includes

- `services/<name>/compose.yaml` — live-faithful runtime definition  
- `services/<name>/.env.example` — placeholders only (no secrets committed)  
- `services/<name>/README.md`  
- `Documentation/services/<name>/` (`*.md` + `service.json`)  
- `scripts/migration/services.conf` row (future Phase 11 classification)  
- `Validation/Phase10.75/<name>/{Migration_Report,Validation,Diff}.md`

## Import rules applied

1. Bind mounts copied from **live** `docker inspect` (authoritative over stale CasaOS YAML).  
2. Images taken from **live** containers when CasaOS YAML drifted (e.g. Radarr hotio vs linuxserver).  
3. CasaOS `x-casaos` blocks and UI icon labels stripped (not required for Docker Compose).  
4. CasaOS `$AppID` path templates expanded to concrete live paths.  
5. Inline DB passwords moved to `.env.example` placeholders (`mariadb`, `nextcloud`).  
6. **No** ownership changes, **no** appdata moves, **no** container recreate.

## Issues discovered

1. **Radarr CasaOS YAML ≠ live:** image and `/downloads` bind differed; import follows live.  
2. **Prowlarr config path** is generic `/DATA/AppData/config` (not service-named) — future migration should target `/mnt/monarch/appdata/prowlarr`.  
3. **Jellyseerr** live is on both `jellyfin_default` and `hotio_default`; CasaOS listed only `jellyfin_default`.  
4. **MariaDB** CasaOS compose contained plaintext passwords — not committed; operators must create local `.env` from `.env.example` before any cutover.  
5. **Byparr** Portainer compose file missing from migrated Portainer volume snapshot — reconstructed from inspect.  
6. **Sonarr** is not running and was not imported (see Missing_Services.md).

## Remaining unmanaged running services

None identified after this import: every running container either already lived under `services/` or was imported here.

Note: some services still **execute** from CasaOS/Portainer/hive paths. Repository import ≠ cutover. Cutover is a later intentional `docker compose up` from `services/<name>` after operator review.

## Intentionally skipped

| Item | Reason |
|---|---|
| Sonarr | No container present |
| Stale CasaOS apps (unused project dirs) | Not running |
| Compose modernization / Traefik labels for *arr | Out of scope |
| Storage migration to `/mnt/monarch/appdata` | Phase 11 |

## Recommended next steps

1. Operator cutover plan: stop CasaOS project → `docker compose -f services/<name>/compose.yaml up -d` one service at a time.  
2. Phase 11 migrate config trees for `prowlarr`, `radarr`, `jellyseerr`, `bazarr`, etc. using new `services.conf` rows.  
3. Rotate MariaDB passwords that appeared in the CasaOS YAML on disk (treat as exposed).  
4. Decide fate of unused CasaOS app directories under `/var/lib/casaos/apps/`.  
5. Proceed to governance modernization once cutovers are complete.
