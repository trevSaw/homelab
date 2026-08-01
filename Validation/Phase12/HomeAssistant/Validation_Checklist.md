---
title: Home Assistant Validation Checklist
document_type: Audit
service: homeassistant
owner: Homelab
status: Active
version: 1.0.0
last_reviewed: 2026-07-31
---

# Validation Checklist — Home Assistant (Phase 12)

Maps to DockerStandard §15 / §16 Definition of Done.

## Automated / CLI

- [ ] `docker compose -f services/homeassistant/compose.yaml config` succeeds
- [ ] Required files exist: `compose.yaml`, `.env.example`, `README.md`, `Versions.md`
- [ ] Governance files exist: `Documentation/services/homeassistant/service.md`, `service.json`
- [ ] External network `proxy` exists on host
- [ ] No plaintext secrets in version-controlled files under `services/homeassistant/`
- [ ] Image tag is exact (grep compose for `latest` / `stable` → none)
- [ ] Healthcheck defined
- [ ] `restart: unless-stopped` present
- [ ] Logging options comply with §12 (`10m` / `5`)

## Runtime

- [ ] `docker ps --filter name=^homeassistant$` shows Up (healthy)
- [ ] `docker inspect --format '{{.State.Health.Status}}' homeassistant` → `healthy`
- [ ] Container attached **only** to `proxy` (no unexpected networks)
- [ ] `docker port homeassistant` empty (no published ports)
- [ ] Traefik router visible for Host `homeassistant.fatherfankscloud.uk`
- [ ] `curl -fsSI https://homeassistant.fatherfankscloud.uk/` returns success TLS response
- [ ] In-container: `curl -fsS http://127.0.0.1:8123/` succeeds

## Governance / architecture

- [ ] Storage only under `/mnt/monarch/appdata/homeassistant`
- [ ] ADR-0003 accepted for networking model
- [ ] Documented security exceptions match running compose
- [ ] Backup target `/hive/backups/homeassistant/` documented and writable
- [ ] INDEX / ServiceIndex entries updated

## Verdict

- [ ] **PASS**
- [ ] **PASS WITH DOCUMENTED EXCEPTIONS** (list below)
- [ ] **FAIL** (blockers below)

Exceptions / blockers:

```
(operator notes)
```

**Validated by:** ________________ **Date:** ________________
