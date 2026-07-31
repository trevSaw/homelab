# Rollback — Prowlarr Phase 12.2D

1. Stop new stack:
   ```bash
   cd /home/fatherfrank/projects/homelab/services/prowlarr
   docker compose -f compose.yml down
   ```
2. Restore config:
   ```bash
   rsync -aH --delete /hive/backups/prowlarr/pre-12.2D-<TIMESTAMP>/ /DATA/AppData/config/
   ```
3. Recreate prior CasaOS/`hotio_default`-only deployment mounting `/DATA/AppData/config`, port `9696`.
4. Validate UI `:9696` and indexer count 10.

Appdata at `/mnt/monarch/appdata/prowlarr` may remain for forensics.
