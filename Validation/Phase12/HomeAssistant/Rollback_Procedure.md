---
title: Home Assistant Rollback Procedure
document_type: Runbook
service: homeassistant
owner: Homelab
status: Active
version: 1.0.0
last_reviewed: 2026-07-31
---

# Rollback Procedure — Home Assistant (Phase 12)

Use when a deploy or upgrade leaves HA unhealthy, misconfigured, or data-corrupt.

## A. Rollback compose / image only (config retained)

1. Identify last known-good image pin from `Versions.md` / git history.
2. Set `image:` in `services/homeassistant/compose.yaml` to that pin.
3. Recreate:

```bash
cd /home/fatherfrank/projects/homelab/services/homeassistant
docker compose -f compose.yaml pull
docker compose -f compose.yaml up -d
```

4. Confirm healthcheck and Traefik UI.

Note: Home Assistant may refuse downgrade if `/config` schema already migrated.
If so, use section B (restore appdata from pre-upgrade backup).

## B. Restore appdata from backup

```bash
cd /home/fatherfrank/projects/homelab/services/homeassistant
docker compose -f compose.yaml down

# Replace <STAMP> with the backup directory name
rsync -aH --delete \
  "/hive/backups/homeassistant/appdata-<STAMP>/" \
  /mnt/monarch/appdata/homeassistant/

# Optionally also restore matching compose pin from git
docker compose -f compose.yaml up -d
```

Validate:

```bash
docker inspect --format '{{.State.Health.Status}}' homeassistant
curl -fsSI https://homeassistant.fatherfankscloud.uk/
```

## C. Full remove (no HA service)

```bash
cd /home/fatherfrank/projects/homelab/services/homeassistant
docker compose -f compose.yaml down
# Retain /mnt/monarch/appdata/homeassistant and /hive/backups for forensics unless
# destruction is explicitly approved.
```

## Post-rollback

- [ ] Health `healthy`
- [ ] Automations / integrations smoke-tested
- [ ] Record incident notes under `Validation/Phase12/HomeAssistant/` if production impact
- [ ] Do not delete the failed backup until a newer verified backup exists
