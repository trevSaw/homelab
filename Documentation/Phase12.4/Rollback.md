# Rollback — Phase 12.4

## Jellyfin

```bash
cd services/jellyfin
# restore prior compose from git if needed, then:
docker compose -f compose.yml up -d
```
Data already on `/mnt/monarch/appdata/jellyfin` — no `/DATA` restore.

## Jellyseerr

```bash
cd services/jellyseerr && docker compose -f compose.yml down
rsync -aH --delete /hive/backups/jellyseerr/pre-12.4-<TS>/ /DATA/AppData/jellyseerr/config/
# recreate prior CasaOS/hotio+jellyfin_default deployment mounting /DATA/...
```

## Bazarr

```bash
cd services/bazarr && docker compose -f compose.yml down
rsync -aH --delete /hive/backups/bazarr/pre-12.4-<TS>/ /DATA/AppData/bazarr/config/
# recreate prior hotio-only CasaOS deployment
```
