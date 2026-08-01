---
title: Home Assistant Service README
document_type: README
service: homeassistant
owner: Homelab
status: Active
version: 1.0.0
last_reviewed: 2026-07-31
related_documents:
  - ADR-0003 Home Assistant Networking
  - Documentation/services/homeassistant/service.md
  - Validation/Phase12/HomeAssistant/
---

# Home Assistant

## Overview & purpose

Home Assistant Core for smart-home automation. Production source of truth is
`services/homeassistant/` with persistent config on
`/mnt/monarch/appdata/homeassistant` (Phase 12 interim layout per DockerStandard §3).

Category: Smart Home / domain `automation`. Ingress: Traefik on the `proxy`
network only (`homeassistant.fatherfankscloud.uk` → container port `8123`).

## Architecture

```text
Internet / LAN clients
        │
        ▼
   Traefik (proxy)
        │  TLS terminate (websecure + le)
        ▼
 homeassistant:8123  ── bind ──► /mnt/monarch/appdata/homeassistant:/config
```

Networking decision and host-network exception path: **ADR-0003**.

## Required external resources

| Resource | Requirement |
|---|---|
| Docker network `proxy` | External; must exist before `compose up` |
| Bind path `/mnt/monarch/appdata/homeassistant` | Created on host; owner suitable for container UID 0 |
| Traefik on `proxy` | Docker provider + `le` certresolver |
| DNS | `homeassistant.fatherfankscloud.uk` → Traefik / host |

No host ports. No named Docker volumes. No `/hive` mounts (config-only service).

## Installation / deployment

```bash
sudo mkdir -p /mnt/monarch/appdata/homeassistant
cd /home/fatherfrank/projects/homelab/services/homeassistant
cp -n .env.example .env
# edit .env (TZ at minimum)
docker compose -f compose.yaml config >/dev/null
docker compose -f compose.yaml up -d
```

After first boot, merge Traefik trust settings from
`config/configuration.yaml.example` into `/mnt/monarch/appdata/homeassistant/configuration.yaml`,
then restart:

```bash
docker compose -f compose.yaml restart
```

Full deployment checklist: `Validation/Phase12/HomeAssistant/Deployment_Checklist.md`.

## Configuration

| Item | Value |
|---|---|
| Compose | `compose.yaml` (Compose Specification; no `version:` field) |
| Env template | `.env.example` → local `.env` (gitignored) |
| Image pin | See `Versions.md` (`2026.7.4`) |
| Config mount | `/mnt/monarch/appdata/homeassistant:/config` |
| Internal listen | `8123` (not published on host) |
| Public URL | `https://homeassistant.fatherfankscloud.uk` |

Secrets (long-lived tokens, integrations) MUST live only in `.env` or inside
`/config` on appdata — never in compose or git.

## Backup procedure

Per BackupStandard / Phase 12 practice: snapshot appdata to `/hive/backups`.

```bash
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
mkdir -p /hive/backups/homeassistant
docker compose -f /home/fatherfrank/projects/homelab/services/homeassistant/compose.yaml stop
rsync -aH /mnt/monarch/appdata/homeassistant/ \
  "/hive/backups/homeassistant/appdata-${STAMP}/"
docker compose -f /home/fatherfrank/projects/homelab/services/homeassistant/compose.yaml start
```

Verify backup contains `configuration.yaml` and `.storage/` before discarding older copies.

## Restore procedure

```bash
cd /home/fatherfrank/projects/homelab/services/homeassistant
docker compose -f compose.yaml down
rsync -aH --delete "/hive/backups/homeassistant/appdata-<STAMP>/" \
  /mnt/monarch/appdata/homeassistant/
docker compose -f compose.yaml up -d
```

Confirm healthcheck healthy and UI via Traefik before declaring restore complete.
See `Validation/Phase12/HomeAssistant/Rollback_Procedure.md`.

## Upgrade procedure

1. Backup appdata (above).
2. Edit `Versions.md` and `compose.yaml` image tag to the new **pinned** release (never `latest` / `stable`).
3. `docker compose -f compose.yaml pull`
4. `docker compose -f compose.yaml up -d`
5. Watch logs and health: `docker inspect --format '{{.State.Health.Status}}' homeassistant`
6. Open UI; confirm integrations and automations.

Home Assistant Core upgrades are one-way for some schema changes — keep the
pre-upgrade backup until validation passes.

## Health verification

```bash
docker inspect --format '{{.State.Status}} {{.State.Health.Status}}' homeassistant
docker compose -f compose.yaml ps
curl -fsS -o /dev/null -w '%{http_code}\n' https://homeassistant.fatherfankscloud.uk/
# or from host into container:
docker exec homeassistant curl -fsS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8123/
```

Expected: container `running`, health `healthy`, HTTPS `200` (or redirect to onboarding on first boot).

## Documented exceptions

| Topic | Exception | Justification |
|---|---|---|
| `user:` non-root | Omitted | Official HA image expects root |
| `read_only: true` | Omitted | Image writes outside `/config` |
| `cap_drop: ALL` | Omitted | Breaks upstream runtime assumptions |
| `network_mode: host` | Not used | ADR-0003; discovery/USB may need future approved exception |
| Compose tree `compose/<domain>/` | Using `services/homeassistant/` | DockerStandard §3 Phase 12 interim SoT |
| Naming `media-*` style | Service/container `homeassistant` | Matches Phase 12 pilot naming + appdata folder |

## Known limitations & troubleshooting

- **mDNS / SSDP / discovery**: bridge/`proxy` networking limits LAN device discovery. Prefer explicit IP integrations, or file an Architecture-approved host-network exception (ADR-0003).
- **USB Zigbee/Z-Wave**: not mounted by default. Adding `devices:` requires README update + Architecture sign-off (Security §9).
- **HTTP 400 through Traefik**: Home Assistant rejects `X-Forwarded-For` from an untrusted source. Set `http.use_x_forwarded_for` + `http.trusted_proxies` to the `proxy` CIDR (`docker network inspect proxy`), then restart.
- **Container restart loop, exit 126, `/run/s6/basedir/bin/init: Permission denied`**: the `/run` tmpfs must carry the `exec` option because Docker mounts tmpfs `noexec` by default and s6-overlay executes its init from `/run`.
- **Traefik `404 page not found`**: no router matched — the container is not running, is not on `proxy`, or lacks `traefik.enable=true` (Traefik runs with `exposedbydefault=false`).
- **Unhealthy after upgrade**: check `docker logs homeassistant`, restore from last good backup if schema migration fails.

Governance catalog: `Documentation/services/homeassistant/service.md` + `service.json`.
