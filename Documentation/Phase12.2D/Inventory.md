# Phase 12.2D — Prowlarr Inventory (pre-cutover)

**Captured:** 2026-07-31

| Field | Value |
|---|---|
| Install type | Docker |
| CasaOS project | `glorious_thomas` |
| Compose | `/var/lib/casaos/apps/glorious_thomas/docker-compose.yml` |
| Image | `ghcr.io/hotio/prowlarr:latest` |
| Version | `2.3.5.5327` (master) |
| App data | `/DATA/AppData/config` (~76M) |
| Ownership | `fatherfrank:fatherfrank` (1000:1000) |
| Network | `hotio_default` (`172.27.0.6`) |
| Port | `9696` |
| Indexers | 10 |
| Applications | Sonarr (`192.168.50.44:8989`), Radarr (stale IPs `172.27.0.5` / `172.27.0.3`) |
| Auth | Forms / DisabledForLocalAddresses |
| Traefik | none |
