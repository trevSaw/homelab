# Production Baseline — Phase 12 Closeout

**Effective:** 2026-07-31  
**Host:** mocha  
**Authority:** This document + `Validation/Phase12.5/` inventory captures  

Future phases (especially Phase 13 AI) MUST treat this as the starting production state unless an explicit change ticket updates it.

## Host & control plane

| Item | Baseline |
|---|---|
| Compose SoT (Phase 12 stacks) | Git repo `services/<service>/` |
| App state | `/mnt/monarch/appdata/<service>` |
| Bulk media / downloads | `/hive/...` (legacy paths in use; canonical target `/hive/media` documented) |
| Ingress | Traefik `v3.6.7` on `proxy`, ports 80/443 |
| Identity | Authentik on `proxy` + `authentic_authentik` |
| Container engine | Docker Compose projects; 42 containers running at closeout |

## Production architecture (summary)

```text
Users ──► Traefik (proxy) ──► user-facing apps (Jellyfin, *arr UIs, Authentik, …)
                │
                └── dual-homed *arr also on hotio_default ──► qbittorrent / NZBGet(VPN netns)
Sonarr (exception): host network + localhost downloaders
```

## Platforms in production

See `Platform_Architecture.md`.

## Security posture (as of closeout)

- Secrets: dedicated `.env` (gitignored) on Phase 12 stacks; no shared symlink `.env` for those services  
- Traefik TLS via Let's Encrypt (`le` resolver); ACME at `/mnt/monarch/appdata/traefik/acme.json`  
- Authentik available; *arr Traefik routers generally lack forward-auth middleware yet  
- Docker socket: Traefik/Portainer/Beszel-agent exceptions documented in Phase 12.1  
- VPN: qBittorrent Hotio WireGuard; NZBGet shares that netns  

## Operational standards

- Pin images; recreate from repo compose  
- Prefer Traefik hostnames over host ports  
- Prefer Docker DNS (`qbittorrent`, `radarr`, `prowlarr`, `jellyfin`) over IPs/`localhost`  
- Document exceptions in phase Known_Exceptions / `Technical_Debt.md`  
- Backups for Phase 12 cutovers under `/hive/backups/<service>/`  

## What Phase 13 builds upon

- Stable Traefik + Authentik edge  
- Media automation + consumption fabric validated (12.3/12.4)  
- Monarch appdata convention  
- Known AI containers already present (Ollama, Open WebUI, Hermes, Honcho, Odysseus) but **not** Phase-12-standardized — see Deferred Work  
