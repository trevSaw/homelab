# Phase 12.2B — Migration Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Migration source | `/var/lib/sonarr` only | Live production DB (214 series, main) |
| Abandoned path | Ignore `/hive/Hotio/sonarr` | Stale develop instance (15 series) |
| Image | `lscr.io/linuxserver/sonarr:version-3.0.10.1566` | Exact native release; avoids v4 schema upgrade during cutover |
| Compose filename | `compose.yml` | Matches Phase 12.1/12.2A SoT (not `docker-compose.yml`) |
| Network | `network_mode: host` | Preserves `localhost` download-client endpoints without DB edits |
| Config mount | `/mnt/monarch/appdata/sonarr:/config` | Phase 12 appdata standard |
| TV / downloads mounts | Bind same host paths into container | Root folders + remote path locals unchanged |
| Ownership | PUID/PGID `1000` | Matches `fatherfrank:fatherfrank` |
| Secrets | Stay in Sonarr DB/`config.xml` under appdata | Not copied into git `.env` |
| v4 upgrade | Deferred | Separate change after soak |
| Scope | Sonarr only | No *arr / Jellyfin / media moves |
