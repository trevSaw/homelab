# Rollback — Sonarr Phase 12.2B

If Docker Sonarr fails validation:

1. Stop container:
   ```bash
   cd /home/fatherfrank/projects/homelab/services/sonarr
   docker compose down
   ```
2. Restore data from backup (example path recorded in validation):
   ```bash
   # Read exact path from Validation/Phase12.2B/sonarr/02_backup_info.txt
   rsync -aH --delete /hive/backups/sonarr/native-<TIMESTAMP>/ /var/lib/sonarr/
   ```
3. Re-enable and start systemd:
   ```bash
   sudo systemctl enable --now sonarr
   systemctl status sonarr --no-pager
   ```
4. Verify:
   - UI on `:8989`
   - `sqlite3 /var/lib/sonarr/sonarr.db 'SELECT COUNT(*) FROM Series;'` → 214

Optional: leave `/mnt/monarch/appdata/sonarr` in place for forensics; do not point systemd at it.
