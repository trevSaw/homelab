# Phase 12.1 — Production Docker Standardization Pilot — Plan

**Date:** 2026-07-31  
**Status:** In progress  
**Scope:** Traefik, Portainer, Beszel (+ agent), Uptime Kuma only

## Objective

Establish the canonical production Docker pattern that future migrations will copy. This is **not** a full-fleet migration.

## Out of scope (explicit)

Jellyfin, Sonarr, Radarr, NZBGet, qBittorrent/Hotio, Nextcloud, Ollama, Open WebUI, ChromaDB, Odysseus, and all other non-pilot services.

## Canonical pattern (pilot)

| Area | Pattern |
|---|---|
| Compose SoT | Git repo `services/<service>/` (live layout). Full `compose/<domain>/` tree from DockerStandard remains a **later layout migration**. |
| Storage | Persistent app config/state → `/mnt/monarch/appdata/<service>` |
| Env | Committed `.env.example`; live `.env` gitignored; no secrets in compose |
| Images | Pinned version tags (no floating `latest`) |
| Restart | `unless-stopped` |
| Health | Defined where image supports it; documented exemption otherwise |
| Resources | `deploy.resources.limits` defined |
| Networks | Prefer external `proxy` / `internal`; document exceptions (`homelab`, `host`, host ports for edge) |
| Security | docker.sock `:ro` where possible; no privileged; document required socket/host-port exceptions |

## Pilot order (blast radius)

1. **Portainer** — already on appdata + repo; standardize only  
2. **Beszel + agent** — already on appdata; move SoT to repo; pin; secrets out of compose  
3. **Uptime Kuma** — CasaOS → repo + migrate data `/DATA` → appdata  
4. **Traefik** — edge; cut SoT `/hive/traefik` → repo last (after env ready)

## Per-service targets

| Service | Image pin | Storage | Compose SoT today → after |
|---|---|---|---|
| Portainer | `portainer/portainer-ce:2.33.6` | already `/mnt/monarch/appdata/portainer` | repo → hardened repo |
| Beszel | `henrygd/beszel:0.18.7` | already appdata | appdata compose → `services/beszel` |
| Beszel-agent | `henrygd/beszel-agent:0.18.7` | already appdata | appdata compose → `services/beszel_agent` |
| Uptime Kuma | `louislam/uptime-kuma:1.23.10-alpine` | `/DATA/...` → `/mnt/monarch/appdata/uptime-kuma` | CasaOS → `services/uptime-kuma` |
| Traefik | `traefik:v3.6.7` | ACME already appdata | `/hive/traefik` → `services/traefik` |

## Validation

Each service: `Validation/Phase12.1/<service>/` with before/after inspect, steps, compose config, health, rollback.

## Success criteria

- All four pilots launched from repo `services/`  
- App config on `/mnt/monarch/appdata/<service>`  
- `.env.example` present; no secrets committed  
- Known security exceptions documented  
- Roadmap updated: Phase 11 COMPLETE WITH DEFERRED ITEMS; Phase 12.1 pilot active/complete  
