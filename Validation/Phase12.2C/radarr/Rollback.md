# Rollback — Radarr Phase 12.2C

1. Stop new stack:
   ```bash
   cd /home/fatherfrank/projects/homelab/services/radarr
   docker compose -f compose.yml down
   ```
2. Restore config from backup (path in `02_backup_info.txt`):
   ```bash
   rsync -aH --delete /hive/backups/radarr/pre-12.2C-<TIMESTAMP>/ /DATA/AppData/radarr/config/
   ```
3. Recreate previous deployment (CasaOS compose or prior `hotio_default`-only run), e.g. restore mounts to `/DATA/AppData/radarr/config` and network `hotio_default`, image `ghcr.io/hotio/radarr:latest` or pinned tag.
4. Validate UI `:7878` and movie count 231.
5. Re-fix download clients if restored DB still has self-IP (optional immediate fix to `qbittorrent`).

Appdata copy at `/mnt/monarch/appdata/radarr` may be left for forensics.
