# Operational Runbook — Phase 12 Baseline

## Day-2 principles

1. Change Phase 12 stacks **only** via git `services/<service>/`  
2. Keep app state on `/mnt/monarch/appdata/<service>`  
3. Prefer Traefik hostnames; treat host ports as transitional  
4. Prefer Docker DNS names on `hotio`/`proxy`; never hard-code container IPs  
5. After network changes, re-run download-client / application tests  

## Common operations

### Recreate a standardized service

```bash
cd /home/fatherfrank/projects/homelab/services/<service>
docker compose -f compose.yml up -d   # or compose.yaml where that is SoT
```

### Order note (downloaders)

1. Recreate `Hotio` (qbittorrent)  
2. Recreate `NZBGet` (depends on qbittorrent netns)  

### Sonarr special case

Sonarr uses host networking. Prowlarr/Jellyseerr/Bazarr reach it via `192.168.50.44:8989`. Changing Sonarr networking requires updating those integrations in the same change window.

### Rollbacks

Phase cutover backups live under `/hive/backups/<service>/`. Per-phase Rollback.md files remain under `Validation/Phase12.2*/` and `Documentation/Phase12.4/Rollback.md`.

## Health quick checks

| Service | Check |
|---|---|
| Traefik | `docker inspect traefik` healthy; :80/:443 up |
| Jellyfin | `http://127.0.0.1:8096/health` + Traefik host |
| Radarr/Prowlarr/Sonarr | `/ping` on service ports |
| qBittorrent | `:8080` |
| NZBGet | `:6789` (auth 401 expected) |

## Where to look

| Need | Location |
|---|---|
| Media networking rules | `Architecture/media-stack-networking.md` |
| Docker standard | `Architecture/standards/DockerStandard.md` |
| Phase evidence | `Documentation/Phase12.*` / `Validation/Phase12.*` |
| This baseline | `Documentation/Phase12.5/` |
