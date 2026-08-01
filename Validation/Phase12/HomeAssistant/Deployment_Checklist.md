---
title: Home Assistant Deployment Checklist
document_type: Audit
service: homeassistant
owner: Homelab
status: Active
version: 1.0.0
last_reviewed: 2026-07-31
---

# Deployment Checklist — Home Assistant (Phase 12)

Operator MUST complete every item before declaring production ready.

## Pre-flight

- [ ] Read `services/homeassistant/README.md` and ADR-0003
- [ ] Confirm Docker network `proxy` exists: `docker network inspect proxy`
- [ ] Confirm Traefik is healthy on `proxy` with Docker provider + `le` resolver
- [ ] Confirm DNS `homeassistant.fatherfankscloud.uk` points at the Traefik endpoint
- [ ] Create appdata: `sudo mkdir -p /mnt/monarch/appdata/homeassistant`
- [ ] Copy env: `cp -n services/homeassistant/.env.example services/homeassistant/.env`
- [ ] Set `TZ` in `.env`
- [ ] Confirm no secrets committed: `git status` / `git check-ignore -v …/.env`

## Compose compliance

- [ ] File is `compose.yaml` (Compose Spec; no `version:` field)
- [ ] Image pinned (not `latest` / `stable`): see `Versions.md`
- [ ] `restart: unless-stopped`
- [ ] Healthcheck present with `test`, `interval`, `timeout`, `retries`, `start_period`
- [ ] Logging `max-size: 10m`, `max-file: 5`
- [ ] Resource limits set (`cpus`, `memory`)
- [ ] Only approved bind: `/mnt/monarch/appdata/homeassistant:/config`
- [ ] No `ports:` mappings
- [ ] No `privileged: true`
- [ ] Traefik labels present (`enable`, `docker.network=proxy`, Host rule, `websecure`, `certresolver=le`, LB `8123`)
- [ ] `docker compose -f compose.yaml config` exits 0

## Deploy

- [ ] `docker compose -f compose.yaml pull`
- [ ] `docker compose -f compose.yaml up -d`
- [ ] Container `running` and health progresses to `healthy` (allow `start_period`)
- [ ] Merge Traefik trust keys from `config/configuration.yaml.example` into live `configuration.yaml`
- [ ] `docker compose -f compose.yaml restart` after trust config
- [ ] HTTPS UI loads at `https://homeassistant.fatherfankscloud.uk`
- [ ] Complete onboarding / restore snapshot if migrating an existing HA

## Post-deploy evidence

- [ ] Capture `docker compose -f compose.yaml config` → validation evidence file
- [ ] Capture `docker inspect homeassistant` (scrub secrets) if required by audit
- [ ] Sign off Validation Checklist and Configuration Verification

**Deployed by:** ________________ **Date:** ________________
