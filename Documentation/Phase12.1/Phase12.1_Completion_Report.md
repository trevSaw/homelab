# Phase 12.1 — Completion Report

**Date:** 2026-07-31  
**Verdict:** **PILOT COMPLETE**  
**Scope:** Traefik, Portainer, Beszel (+ agent), Uptime Kuma only

## Summary

The production Docker standardization pilot is live. All four pilot services now:

- launch from git `services/<name>/`
- use pinned image tags
- keep application state under `/mnt/monarch/appdata/<service>` (Uptime Kuma newly migrated)
- ship `.env.example` + README + Versions
- document security exceptions

Non-pilot services were **not** modified.

## Results by service

| Service | Compose SoT | Image pin | Appdata | Health / smoke | Notes |
|---|---|---|---|---|---|
| Portainer | `services/portainer` | `2.33.6` | already | `/api/status` 200 | Healthcheck exempt (distroless) |
| Beszel | `services/beszel` | `0.18.7` | already | HTTP 200 | `homelab` network exception |
| Beszel-agent | `services/beszel_agent` | `0.18.7` | already | running | secrets moved out of compose |
| Uptime Kuma | `services/uptime-kuma` | `1.23.10-alpine` | **migrated** | healthy; HTTP 302 | CasaOS retired for this app |
| Traefik | `services/traefik` | `v3.6.7` | ACME already | healthy; ping OK | cut over from `/hive/traefik` |

## Volume migrations performed

| Service | From | To |
|---|---|---|
| Uptime Kuma | `/DATA/AppData/uptimekuma/app/data` | `/mnt/monarch/appdata/uptime-kuma` |

Others needed no data move (already on appdata from Phase 11 / prior).

## Canonical pattern proven

1. **SoT:** `services/<service>/compose.y*ml` in git  
2. **Storage:** `/mnt/monarch/appdata/<service>` for config/state  
3. **Env:** `.env.example` committed; `.env` gitignored; no secrets in compose  
4. **Ops:** pinned tags, `unless-stopped`, logging rotation, memory limits  
5. **Security:** sock `:ro` where possible; required exceptions catalogued  

Full `compose/<domain>/…` directory layout from DockerStandard remains **deferred** — pilot freezes `services/` as the live canonical path.

## Lesson learned (critical)

`services/traefik/.env` was a **symlink to `services/.env`** (shared with Authentik/Homepage). Writing a Traefik-only env through that path overwrote the shared file.  

**Remediation:** restored shared `services/.env` from live Authentik container + hive Traefik values; replaced Traefik symlink with a dedicated `.env`. Authentik remained healthy throughout.  

**Rule for future pilots:** never assume `services/<svc>/.env` is dedicated — check for symlinks before writing.

## Artifacts

- Plan: `Documentation/Phase12.1/Phase12.1_Plan.md`
- Exceptions: `Documentation/Phase12.1/Known_Exceptions.md`
- Per-service validation: `Validation/Phase12.1/<service>/`
- Roadmap: Phase 11 → Complete with Deferred Items; Phase 12.1 → pilot complete

## Follow-ups (not Phase 12.1 scope)

- Rotate Beszel agent token (was previously plaintext in appdata compose)
- Optional Traefik route for Uptime Kuma / Beszel
- Move remaining stacks to the same pattern in later batches
- Phase 12 secrets/Vault workstream
- Future layout migration to `compose/<domain>/` if still desired

## Rollback pointers

| Service | Rollback |
|---|---|
| Traefik | `/hive/traefik` (+ `compose.yaml.phase12.1.bak`) |
| Portainer | prior `services/portainer/compose.yaml` |
| Beszel | `/mnt/monarch/appdata/beszel/compose.yml` |
| Uptime Kuma | `/DATA/AppData/uptimekuma/app/data.old` + CasaOS project |
