---
title: Home Assistant Service Governance
document_type: README
service: homeassistant
owner: Homelab
status: Active
version: 1.0.0
last_reviewed: 2026-07-31
related_documents:
  - ADR-0003 Home Assistant Networking
  - services/homeassistant/README.md
  - services/homeassistant/Implementation_Notes.md
  - Validation/Phase12/HomeAssistant/
---

# homeassistant

## Overview

- Purpose: Home Assistant Core — smart-home automation and device orchestration
- Category: Smart Home
- Domain (Docker): `automation`
- Current lifecycle state: Deployed and validated on mocha 2026-07-31 (onboarding pending)
- Importance level: High (ServiceIndex long-term smart home)
- Repository SoT: `services/homeassistant/` (Phase 12 interim; DockerStandard §3)
- Persistent data: `/mnt/monarch/appdata/homeassistant`

## Repository location

| Artifact | Path |
|---|---|
| Compose | `services/homeassistant/compose.yaml` |
| Env template | `services/homeassistant/.env.example` |
| Versions | `services/homeassistant/Versions.md` |
| Service README | `services/homeassistant/README.md` |
| Implementation notes | `services/homeassistant/Implementation_Notes.md` |
| Config example (Traefik trust) | `services/homeassistant/config/configuration.yaml.example` |
| Catalog JSON | `Documentation/services/homeassistant/service.json` |
| This document | `Documentation/services/homeassistant/service.md` |
| Validation pack | `Validation/Phase12/HomeAssistant/` |
| Deployment evidence | `Validation/Phase12/HomeAssistant/Deployment_Evidence.md` |
| ADR | `Architecture/decisions/ADR-0003-Home-Assistant-Networking.md` |

## Runtime information

| Field | Value |
|---|---|
| Container name | `homeassistant` |
| Hostname | `homeassistant` |
| Image | `ghcr.io/home-assistant/home-assistant:2026.7.4` |
| Restart policy | `unless-stopped` |
| Networks | `proxy` (external) |
| Published ports | none |
| Listen port (container) | `8123` |
| Traefik Host | `homeassistant.fatherfankscloud.uk` |
| Entrypoint | `websecure` + `tls.certresolver=le` |
| Healthcheck | `curl` HTTP `http://127.0.0.1:8123/` |
| Logging | `max-size: 10m`, `max-file: 5` |
| Resource limits | `cpus: 2.0`, `memory: 2G` |
| Environment files | `.env.example` / `.env` |
| Timezone | `TZ` from `.env` |

## Dependencies

- Docker Engine + Compose v2
- External network `proxy`
- Traefik (TLS + Docker provider) on `proxy`
- DNS for `homeassistant.fatherfankscloud.uk`
- Host path `/mnt/monarch/appdata/homeassistant`

No runtime dependency on media stack (`hotio`), Sonarr, or Jellyfin.

## Storage

| Mount | Host | Container | Class |
|---|---|---|---|
| Config / state | `/mnt/monarch/appdata/homeassistant` | `/config` | SSD appdata (Architecture storage policy) |
| tmpfs | — | `/tmp`, `/run` (`exec` required for s6-overlay init) | ephemeral |

No bind mounts outside approved storage locations.

## Networking

- Sole attachment: `proxy`
- Ingress: Traefik only (Architecture reverse-proxy rules)
- Host networking: **not used** — see ADR-0003
- Discovery / USB: deferred; requires approved exception before enablement

## Security

- Pinned image tag (no `latest`)
- No privileged mode
- `security_opt: no-new-privileges:true`
- Secrets via `.env` / `/config` only
- Documented exceptions: root user, non-`read_only` rootfs, no full `cap_drop`

## Operations

Procedures live in `services/homeassistant/README.md`:

- Backup → `/hive/backups/homeassistant/`
- Restore
- Upgrade (pin bump)
- Health verification

Validation/rollback: `Validation/Phase12/HomeAssistant/`.

## Risks

| Risk | Mitigation |
|---|---|
| Limited LAN discovery on bridge | ADR-0003; explicit integrations; future host-net exception if required |
| Core schema upgrades irreversible without backup | Mandatory pre-upgrade rsync |
| Missing `trusted_proxies` breaks Traefik UX | Example config + Configuration Verification checklist |
| Root container | Isolate on `proxy`; no host ports; no privileged |

## ADR references

- ADR-0003 — Home Assistant networking (proxy/bridge vs host)

## Evidence

- Phase: Phase 12 Home Assistant packaging
- Image digest recorded in `Versions.md` (2026-07-31)
- Compose validated with `docker compose config` prior to deploy sign-off

## Documentation status

`present` — governance fields populated; stack deployed and validated 2026-07-31.
