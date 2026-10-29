# searxng

Internal-only metasearch research service for KORA/Hermes (Phase 5).

## Overview
- Purpose: private, keyless web-search backend for KORA/Hermes research.
- Category: AI / Search
- Current lifecycle state: Production (validated 2026-10-06)
- Importance level: Standard
- Canonical documentation: `services/searxng/README.md`
- Decision: `Architecture/decisions/ADR-0014-SearXNG-Internal-Research-Service.md`

## Repository Location
- Service directory: `services/searxng/`
- Compose file: `services/searxng/compose.yaml`
- Settings: `services/searxng/config/settings.yml` (secret-free, JSON enabled)
- Environment template: `services/searxng/.env.example`

## Runtime Information
- Container name: `searxng`
- Image: `searxng/searxng:2026.5.31-7159b8aed` (pinned)
- Ports: none published (`:8080` internal only)
- Networks: `ollama_ollama-net` (external, internal AI fabric)
- Volumes: `/mnt/monarch/appdata/searxng` → `/var/cache/searxng` (rw);
  `/home/fatherfrank/projects/homelab/services/searxng/config` → `/etc/searxng:ro`
  (absolute paths required by the docker-admin deploy path)
- Restart policy: `unless-stopped`
- Hardening: `cap_drop: [ALL]` + `CHOWN/SETGID/SETUID/DAC_OVERRIDE`;
  `no-new-privileges`

## Secrets
- `SEARXNG_SECRET` — instance secret in the gitignored `.env`; overrides
  `server.secret_key`. Never committed, logged, or exposed.

## Exposure
None. No published ports, no Traefik route (`traefik.enable=false`), no DNS
record. Reachable only from containers on `ollama_ollama-net` (principally
Hermes).

## Validation
Health `healthy`; `/healthz` → `OK`; JSON search via
`/search?q=<query>&format=json`; no external listener.
