---
title: Home Assistant Implementation Notes
document_type: Audit
service: homeassistant
owner: Homelab
status: Active
version: 1.0.0
last_reviewed: 2026-07-31
related_documents:
  - ADR-0003 Home Assistant Networking
  - Architecture/standards/DockerStandard.md
---

# Implementation Notes — Home Assistant

## Purpose

Record how this stack maps repository governance to a concrete Compose
deployment without inventing new standards.

## Standards applied (existing only)

| Standard | How applied |
|---|---|
| Homelab Architecture Standard | SSD config on `/mnt/monarch`; ingress via reverse proxy; no direct host ports |
| Docker Compose Standard | `compose.yaml`, no `version:`, key order §4, `.env.example`, `README.md`, `Versions.md`, healthcheck, logging §12 (`10m`/`5`), `restart: unless-stopped`, pinned image, `deploy.resources` |
| Networking (Architecture + Docker §6) | External `proxy` only; Traefik labels §13 |
| Storage | Single approved bind: `/mnt/monarch/appdata/homeassistant:/config` |
| Security | No `latest`; no privileged; no plaintext secrets in git; `.env` for env; `no-new-privileges`; documented exceptions for root/`read_only` |
| Logging | json-file rotation via compose `logging.options`; label `com.homelab.logging=central` |
| Naming | Folder/service/container `homeassistant` (Phase 12 interim pattern) |
| Documentation | `Documentation/services/homeassistant/{service.md,service.json}`; YAML front-matter where required |
| Validation | `Validation/Phase12/HomeAssistant/` checklists |
| ADR Standard | ADR-0003 for networking trade-off vs official host-network recommendation |
| Backup Standard | Appdata rsync to `/hive/backups/homeassistant/` |

## Compose filename

DockerStandard §3 requires **`compose.yaml`**. That file is the deliverable
equivalent of a generic `docker-compose.yml`. Operators MUST use:

```bash
docker compose -f compose.yaml …
```

Do not introduce a second compose file that can drift.

## Image pin

`ghcr.io/home-assistant/home-assistant:2026.7.4` (digest recorded in `Versions.md`).
Tag chosen as current Core release at authoring date 2026-07-31; upgrades are
manual pin bumps only.

## Traefik

Labels mirror Phase 12 media UI pattern (`traefik.enable`, `traefik.docker.network=proxy`,
`Host(...)`, `websecure`, `tls.certresolver=le`, LB port **8123**). Domain:
`homeassistant.fatherfankscloud.uk`.

HA must trust the proxy network CIDR in `configuration.yaml` (see
`config/configuration.yaml.example`). Without `trusted_proxies`, HA may reject
or mishandle `X-Forwarded-*` headers.

## Storage layout

```text
/mnt/monarch/appdata/homeassistant/     # entire HA /config tree
  configuration.yaml
  automations.yaml   # if split
  .storage/
  home-assistant_v2.db
  …
```

No binds under `/DATA`, `/hive` (except backups), or anonymous volumes.

## Security exceptions (approved for this stack)

1. Process runs as root (upstream image).
2. Root filesystem not `read_only` (upstream writes outside `/config`).
3. Capabilities not fully dropped.
4. Host networking not enabled (preferred for governance); discovery/USB deferred.

Hardening that **is** applied: `no-new-privileges`, no privileged mode, no
published ports, tmpfs for `/tmp` and `/run`, memory/CPU limits, pinned image.

## Out of scope (this delivery)

- Live cutover of an existing HA instance (none assumed present).
- Zigbee/Z-Wave USB passthrough.
- Add-on Supervisor / HA OS (Core container only).
- Authentik/forward-auth middleware (may be added later via Traefik static config).

## Validation status

Deployed and validated on mocha 2026-07-31 (see
`Validation/Phase12/HomeAssistant/Deployment_Evidence.md`): container healthy,
Traefik router live, HTTPS `302 → /onboarding.html 200` with the Let's Encrypt
`fatherfankscloud.uk` certificate.

## Runtime findings from first deployment

| Finding | Resolution |
|---|---|
| Container looped with exit 126 and `/run/s6/basedir/bin/init: Permission denied` | Docker mounts `tmpfs` with `noexec`; s6-overlay executes init from `/run`. Added `exec` to the `/run` tmpfs options. `/tmp` keeps the hardened default. |
| Traefik returned HTTP 400 after the router matched | Home Assistant refused `X-Forwarded-For` from an untrusted source. Installed `http.use_x_forwarded_for` + `trusted_proxies: 172.19.0.0/16` (live `proxy` subnet) into `/config/configuration.yaml`. |
| Traefik returned `404 page not found` before first start | Expected: with `providers.docker.exposedbydefault=false`, no router exists until the labelled container runs on `proxy`. |
