# docker-admin

Narrow, token-authenticated Docker administration helper for KORA/Hermes
(Phase 3).

## Overview
- Purpose: let KORA inspect live Docker state and perform controlled
  restart/recreate/deploy **without** giving Hermes the Docker socket.
- Category: AI / Administration Boundary
- Current lifecycle state: Production
- Importance level: High
- Canonical documentation: `services/docker-admin/README.md`
- Decision: `Architecture/decisions/ADR-0012-KORA-Controlled-Docker-Administration.md`
- Phase report: `Documentation/Phase3/KORA_Controlled_Administration.md`

## Repository Location
- Service directory: `services/docker-admin/`
- Compose file: `services/docker-admin/compose.yaml`
- Environment template: `services/docker-admin/.env.example`
- Implementation: `services/docker-admin/app.py`

## Runtime Information
- Container name: `docker-admin`
- Image: `homelab/docker-admin:1.0.0` (built from `Dockerfile`, `python:3.12-slim`)
- User: `1000:1000` (repo owner, reads `/repo` 0600 `.env` for Compose) + group `999` (host `docker` gid)
- Ports: none published (`8765` on internal `kora-admin` network only)
- Networks: `kora-admin` (internal)
- Volumes: `/var/run/docker.sock` (rw — the only socket on the KORA admin
  path), `/home/fatherfrank/projects/homelab:/repo:ro`, host Docker CLI +
  compose plugin (ro)
- Restart policy: `unless-stopped`
- Hardening: read-only rootfs, `cap_drop: [ALL]`, `no-new-privileges`

## Secrets
- `DOCKER_ADMIN_TOKEN` — bearer token in the gitignored `.env`; the same value
  is written to the Hermes volume file `/opt/data/docker-admin.token`. Never
  committed, logged, or returned.
