# Phase 12.3 — Platform Validation Report

**Date:** 2026-07-31  
**Type:** Validation only (no migrations, recreates, or config changes)  
**Scope:** Media **automation** platform baseline after 12.2A–12.2D  
**Services:** qBittorrent, NZBGet, Sonarr, Radarr, Prowlarr (+ Traefik as ingress)

## Verdict

**PASS WITH DOCUMENTED EXCEPTIONS**

The automation chain is operational as a single system:

- Prowlarr ↔ Sonarr / Radarr application tests PASS  
- Sonarr / Radarr ↔ qBittorrent / NZBGet download-client tests PASS  
- ApplicationIndexerSync PASS  
- Radarr / Prowlarr Traefik HTTPS routers respond  
- All five automation services run from repo compose with appdata on Monarch and pinned images  

Primary remaining fabric debt: **Sonarr still on host networking** (not yet on `proxy`/`hotio`), so it uses `localhost` downloaders and LAN URLs from Prowlarr.

---

## Architecture compliance (migrated services)

| Service | Repo compose | Appdata | Pinned image | `.env` / `.env.example` | Exceptions doc |
|---|---|---|---|---|---|
| qBittorrent (Hotio) | `services/Hotio/compose.yml` | `/mnt/monarch/appdata/hotio` | `release-4.5.5` | yes | Phase 12.2A |
| NZBGet | `services/NZBget/compose.yml` | `/mnt/monarch/appdata/nzbget` | digest pin | yes | Phase 12.2A |
| Sonarr | `services/sonarr/compose.yml` | `/mnt/monarch/appdata/sonarr` | `version-3.0.10.1566` | yes | Phase 12.2B |
| Radarr | `services/radarr/compose.yml` | `/mnt/monarch/appdata/radarr` | `release-5.22.4.9896` | yes | Phase 12.2C |
| Prowlarr | `services/prowlarr/compose.yml` | `/mnt/monarch/appdata/prowlarr` | `release-2.3.5.5327` | yes | Phase 12.2D |

No shared/symlink `.env` files detected on these stacks.

---

## Network membership (canonical vs live)

### Expected vs actual

| Service | Expected | Live | Gap |
|---|---|---|---|
| Traefik | `proxy` | `proxy` | — |
| Sonarr | `proxy` + `hotio` | **`host`** | Dual-home pending |
| Radarr | `proxy` + `hotio` | `proxy` + `hotio_default` | — |
| Prowlarr | `proxy` + `hotio` | `proxy` + `hotio_default` | — |
| qBittorrent | `hotio` | `hotio_default` | — |
| NZBGet | `hotio` (named) | Shared netns with qBittorrent | No distinct DNS name |

### Live `proxy` (media-relevant)

`traefik`, `jellyfin`, `radarr`, `prowlarr` — **Sonarr absent** (host).

### Live `hotio_default` (media-relevant)

`qbittorrent`, `radarr`, `prowlarr`, (+ Bazarr/Jellyseerr/Readarr/Byparr not in this baseline) — **Sonarr absent**; **NZBGet** present only via qBittorrent netns.

---

## Service communication

```text
Prowlarr --(LAN 192.168.50.44)-- > Sonarr --(localhost)-- > qBittorrent :8080
                              \                     \--> NZBGet via :6789 (qbit publish)
                               \
                                +--(Docker DNS)-- > Radarr --(qbittorrent:8080 / :6789)-- > downloaders
```

| Link | Mechanism | Result |
|---|---|---|
| Prowlarr → Radarr | `http://radarr:7878` | PASS |
| Prowlarr → Sonarr | `http://192.168.50.44:8989` | PASS (exception) |
| Radarr → qBittorrent | `qbittorrent:8080` | PASS |
| Radarr → NZBGet | `qbittorrent:6789` | PASS (exception: shared netns) |
| Sonarr → qBittorrent | `localhost:8080` | PASS (exception: host net) |
| Sonarr → NZBGet | `localhost:6789` | PASS (exception: host net) |
| Prowlarr ApplicationIndexerSync | command API | PASS (201) |

### Approved exceptions (communication)

1. Sonarr host networking → `localhost` download clients  
2. Prowlarr ↔ Sonarr via host LAN IP  
3. NZBGet reachable as `qbittorrent:6789` / host `:6789`, not `nzbget:6789`

---

## Traefik

| Hostname | Labels | HTTPS probe (`--resolve 127.0.0.1:443`) | Middleware / Authentik |
|---|---|---|---|
| `traefik.fatherfankscloud.uk` | dashboard | (edge) | none on media apps |
| `radarr.fatherfankscloud.uk` | yes (`proxy`, le) | **200** | none |
| `prowlarr.fatherfankscloud.uk` | yes | **200** | none |
| `jellyfin.fatherfankscloud.uk` | yes (consumption) | **302** | none observed on labels |
| Sonarr | **none** | N/A — host `:8989` | — |

ACME store present: `/mnt/monarch/appdata/traefik/acme.json`.  
Cert resolver: `le` on Radarr/Prowlarr/Jellyfin routers.  
No Authentik forward-auth middleware attached to *arr routers yet.

### Transitional host ports

| Port | Service | Note |
|---|---|---|
| 80/443 | Traefik | Required edge |
| 8080/8118/6789 | qBittorrent (+ NZBGet on 6789) | Operator / shared netns |
| 8989 | Sonarr | Host network only ingress |
| 7878 | Radarr | Transitional beside Traefik |
| 9696 | Prowlarr | Transitional beside Traefik |
| 8096 | Jellyfin | Consumption layer; Traefik also present |

---

## Automation test summary

| Test | Result |
|---|---|
| Sonarr UI / DB (214 series) | PASS |
| Radarr UI / DB (231 movies) | PASS |
| Prowlarr UI / DB (10 indexers) | PASS |
| Download-client tests (both *arr) | PASS |
| Prowlarr app tests | PASS |
| Indexer samples | Mostly PASS; some remote 400s (Badass Torrents, Internet Archive) — not fabric failures |
| qBittorrent / NZBGet HTTP | PASS / 401 auth |

Evidence: `Validation/Phase12.3/01_architecture_checklist.txt`, `02_communication_config.txt`, `03_automation_tests.txt`, `04_dns_traefik.txt`.

---

## Baseline statement

Phase 12.3 establishes the **media automation platform baseline**. Consumption-layer work (Jellyfin hardening, Jellyseerr, Bazarr, Lidarr) should proceed against `Architecture/media-stack-networking.md` without regressing this automation fabric.
