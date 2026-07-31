# Phase 12 — Final Report

**Date:** 2026-07-31  
**Status:** COMPLETE  
**Closeout:** Phase 12.5 (documentation / validation only — no production changes)

## Verdict

Phase 12 successfully established a production Docker standard and applied it across **core infrastructure**, **media automation**, and **media consumption**. The repository is the Source of Truth for standardized stacks. Application state for those stacks lives under `/mnt/monarch/appdata`. Canonical media networking (`proxy` + `hotio`) is documented and largely implemented.

## Major accomplishments

1. **Phase 12.1** — Traefik, Portainer, Beszel, Uptime Kuma pilot pattern  
2. **Phase 12.2A** — qBittorrent + NZBGet standardization  
3. **Phase 12.2B** — Sonarr native → Docker (appdata preserved, 214 series)  
4. **Phase 12.2C** — Radarr SoT + dual-home + download-client FAIL remediation  
5. **Phase 12.2D** — Prowlarr SoT + dual-home + Traefik  
6. **Media networking standard** — `Architecture/media-stack-networking.md`  
7. **Phase 12.3** — Automation platform validation baseline  
8. **Phase 12.4** — Jellyfin / Jellyseerr / Bazarr consumption standardization  
9. **Phase 12.5** — Production baseline & closeout (this package)

## Architecture improvements

- Dual-network media model: Traefik ingress on `proxy`; automation DNS on `hotio` (`hotio_default`)  
- Pinned images + dedicated `.env` / `.env.example` on Phase 12 stacks  
- Download clients / app integrations moved off hard-coded container IPs where cut over  
- Traefik routers for Jellyfin, Radarr, Prowlarr, Jellyseerr, Bazarr (+ existing edge)  

## Services standardized in Phase 12

Traefik, Portainer, Beszel (+ agent), Uptime Kuma, qBittorrent, NZBGet, Sonarr, Radarr, Prowlarr, Jellyfin, Jellyseerr, Bazarr.

## Remaining technical debt (approved)

See `Technical_Debt.md` — headliners: Sonarr host networking, NZBGet shared VPN netns, transitional host ports, partial fleet still on CasaOS/`latest`/non-appdata.

## Lessons learned

- Never treat abandoned Hive paths as SoT (`/hive/Hotio/sonarr`)  
- Never write service `.env` files that are symlinks to shared env (Traefik incident in 12.1)  
- Shared `network_mode: container:` breaks Docker DNS names (NZBGet)  
- Hard-coded container IPs rot after recreate (Radarr/Bazarr FAILS)  
- Validate download-client / app tests after every network change  

## Recommendations into Phase 13

1. Freeze Phase 12 media/automation fabric unless debt items are intentionally scheduled  
2. Start Phase 13 against `Production_Baseline.md` — do not re-litigate media networking  
3. Queue Sonarr dual-home as a small Phase 12.x hotfix or early maintenance item if it blocks AI/media integrations  

## Package index

| Doc | Purpose |
|---|---|
| `Production_Baseline.md` | Authoritative baseline for Phase 13 |
| `Platform_Architecture.md` | Platforms & purposes |
| `Service_Inventory.md` | Per-service production facts |
| `Storage_Architecture.md` | Monarch / Hive / backups |
| `Network_Architecture.md` | Networks & diagrams |
| `Technical_Debt.md` | Ranked debt |
| `Deferred_Work.md` | Intentionally out of Phase 12 |
| `Operational_Runbook.md` | Day-2 ops pointers |
| `Acceptance_Signoff.md` | Closeout checklist |
