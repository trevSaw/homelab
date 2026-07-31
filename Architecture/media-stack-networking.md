# Media Stack Networking Architecture

**Status:** Canonical standard (amended)  
**Date:** 2026-07-31  
**Amendment:** Phase 12 Architecture Amendment — Media Network Standard  
**Applies to:** All future Phase 12 media migrations  
**Related:** `Architecture/standards/DockerStandard.md`, `Architecture/standards/HomelabArchitectureStandard.md`

This document is the **single source of truth** for media Docker networking. It **supersedes** any earlier media network diagrams or service membership lists from this phase. It does not by itself change running containers.

Future migrations (Radarr, Prowlarr, Jellyfin, Sonarr re-home, etc.) **MUST** target this architecture by default unless a documented technical exception applies.

---

## Objective

- Give user-facing media apps a single HTTPS ingress path via Traefik (`proxy`) + Authentik where appropriate
- Give automation services a private Docker DNS path on `hotio`
- Avoid `network_mode: host` and `localhost` client URLs unless a documented exception exists
- Keep app state on Monarch; keep media and downloads on Hive

---

## Canonical media networks

There are **two** primary Docker networks for the media platform.

```text
                         Internet / LAN users
                                  |
                                  v
                           [ Traefik ]
                            proxy only
                                  |
     +------------+---------------+---------------+------------+
     |            |               |               |            |
     v            v               v               v            v
 [Jellyfin]  [Overseerr*]    [Sonarr]        [Radarr]    [Prowlarr]
 proxy only  proxy only    proxy+hotio     proxy+hotio  proxy+hotio
                                 |               |            |
                                 +-------+-------+------------+
                                         |
                                         v
                                   +-----------+
                                   |   hotio   |  internal automation
                                   +-----------+
                                    |    |    |
                                    v    v    v
                            [qbittorrent] [nzbget] [Bazarr*/Lidarr*]
                             hotio only  hotio only  (+ proxy when UI)

* Overseerr / Bazarr / Lidarr: attach when deployed (see membership table)
```

### 1. `proxy`

| | |
|---|---|
| **Purpose** | Traefik ingress, HTTPS, Authentik authentication, user-facing web applications |
| **Live Docker network** | `proxy` (external, already on host) |
| **Public entrypoints** | **Traefik only** (`80`/`443`) |
| **Access pattern** | `https://<service>.<domain>` via Traefik — not host ports when practical |

**Services attached:**

- Traefik
- Jellyfin
- Sonarr
- Radarr
- Prowlarr
- Bazarr (future, if deployed)
- Lidarr (future, if deployed)
- Overseerr (future, if deployed)

These services should ultimately be reachable through Traefik rather than host ports.

### 2. `hotio`

| | |
|---|---|
| **Purpose** | Internal automation network; Docker DNS instead of localhost / host networking |
| **Logical name** | `hotio` |
| **Live Docker network** | `hotio_default` (external; do not invent a second parallel network) |
| **Public entrypoints** | None |
| **Access pattern** | Service DNS names (examples below) |

**Services attached:**

- Sonarr
- Radarr
- Prowlarr
- qBittorrent
- NZBGet
- Bazarr (future, if deployed)
- Lidarr (future, if deployed)

**DNS examples:**

- `qbittorrent:8080`
- `nzbget:6789`
- `prowlarr:9696`

Compose should attach using the logical name aliased to the live network:

```yaml
networks:
  proxy:
    external: true
  hotio:
    external: true
    name: hotio_default
```

---

## Service membership (canonical)

| Service | `proxy` | `hotio` | Class |
|---|---|---|---|
| Traefik | ✅ | — | Proxy-only |
| Jellyfin | ✅ | — | Proxy-only |
| Overseerr (future, if deployed) | ✅ | — | Proxy-only |
| Sonarr | ✅ | ✅ | Dual-homed |
| Radarr | ✅ | ✅ | Dual-homed |
| Prowlarr | ✅ | ✅ | Dual-homed |
| Bazarr (future, if deployed) | ✅ | ✅ | Dual-homed |
| Lidarr (future, if deployed) | ✅ | ✅ | Dual-homed |
| qBittorrent (Hotio) | — | ✅ | Hotio-only |
| NZBGet | — | ✅ | Hotio-only |

### Dual-homed

Must belong to **both** networks: Sonarr, Radarr, Prowlarr, Bazarr (future), Lidarr (future).

### Proxy-only

Traefik, Jellyfin, Overseerr (future).

### Hotio-only

qBittorrent, NZBGet.

---

## Dual-homed pattern

Dual-homed apps join **both** networks so that:

1. Users reach the UI through Traefik on `proxy`
2. Apps reach downloaders / Prowlarr / peers by name on `hotio`

```yaml
# Illustrative — not a live cutover
services:
  sonarr:
    image: lscr.io/linuxserver/sonarr:<pinned>
    container_name: sonarr
    restart: unless-stopped
    env_file: [.env]
    networks:
      - proxy
      - hotio
    volumes:
      - /mnt/monarch/appdata/sonarr:/config
      - /hive/media:/hive/media
      - /hive/media/downloads:/hive/media/downloads
    labels:
      - traefik.enable=true
      - traefik.docker.network=proxy
      - traefik.http.routers.sonarr.rule=Host(`sonarr.example.com`)
      - traefik.http.routers.sonarr.entrypoints=websecure
      - traefik.http.routers.sonarr.tls=true
      - traefik.http.services.sonarr.loadbalancer.server.port=8989
    # No host ports when Traefik publishes the UI
```

Downloader-only example:

```yaml
services:
  qbittorrent:
    networks:
      - hotio
    # VPN caps/sysctls as required — see Phase 12.2A exceptions
```

---

## Communication rules

| Prefer | Avoid (unless documented exception) |
|---|---|
| `qbittorrent:8080` | `localhost:8080` |
| `nzbget:6789` | `127.0.0.1:6789` |
| `prowlarr:9696` | `host.docker.internal` |
| Traefik `Host()` routers | Publishing app host ports |
| Bridge networks + Docker DNS | `network_mode: host` |
| `traefik.docker.network=proxy` on dual-homed apps | Letting Traefik pick the wrong NIC |

*arr download-client / indexer settings and remote path mappings must use **container-visible** paths and **Docker DNS hostnames** after cutover off host networking.

---

## Storage standard

| Class | Canonical path | Rule |
|---|---|---|
| Application state | `/mnt/monarch/appdata/<service>` | Config, DB, metadata |
| Media libraries | `/hive/media/` | Never move into appdata |
| Downloads | `/hive/media/downloads` | Shared with download clients / *arr |

Identity mounts (same path inside the container as on the host) remain preferred when preserving existing root folders / remote path mappings.

### Transitional paths (today)

Production still uses legacy Hive layouts (e.g. `/hive/jellyfin/tv`, `/hive/downloads`). New migrations should **not** invent a third layout casually; either:

- keep identity mounts to the current live paths and document them as transitional, or
- move path strings in the app DB as an explicit, validated step toward `/hive/media/...`

Do not relocate bulk media as a side effect of a networking-only change.

---

## Traefik

Long-term user access examples:

- `https://sonarr.<domain>`
- `https://radarr.<domain>`
- `https://prowlarr.<domain>`
- `https://jellyfin.<domain>`

Requirements for media UIs on `proxy`:

1. Attach to `proxy`
2. Enable Traefik labels; set `traefik.docker.network=proxy`
3. Do not publish host ports for the UI when a router exists
4. Prefer Authentik / forward-auth middleware for apps that lack strong native auth

Traefik itself remains proxy-only and is the only service that binds public `80`/`443`.

---

## Migration considerations (future cutovers)

Default target for Radarr, Prowlarr, Jellyfin, Sonarr re-home, and related work: **this document**.

1. **Inventory** current networks, host ports, client hostnames (`localhost`?), and path mappings  
2. **Attach networks** (`proxy` and/or `hotio` → `hotio_default`) without deleting data  
3. **Update app settings** from `localhost` to Docker DNS names **before** removing host networking  
4. **Add Traefik labels** and verify router; then drop host port publish  
5. **Validate** UI via Traefik, download-client / indexer tests, root-folder access, import path  
6. **Document** any remaining exception in the phase Known_Exceptions file  

### NZBGet + VPN (critical)

Today NZBGet often uses `network_mode: container:qbittorrent` so Usenet traffic shares the VPN netns. In that mode **other containers cannot resolve `nzbget` as a distinct DNS name**; they must use `qbittorrent:<nzb-port>` (or keep host networking).

Target architecture wants a first-class `nzbget` name on `hotio`. Achieving that without losing VPN egress is a **dedicated design step**. Do not casually break `network_mode: container:qbittorrent` during an unrelated migration.

### Sonarr (Phase 12.2B current state)

Sonarr currently runs `network_mode: host` with `localhost` download clients — a documented temporary exception until a dual-homed `proxy`+`hotio` cutover updates client hostnames and adds Traefik.

### Prowlarr / Radarr (live today)

May already sit on `hotio_default` without `proxy` / Traefik. Future Phase 12 standardization should add `proxy` + Traefik labels for dual-homed membership without abandoning `hotio` DNS.

---

## Documented exceptions

| Exception | Why it exists | Exit criteria |
|---|---|---|
| Live network name `hotio_default` vs logical `hotio` | Existing production bridge | Keep alias in compose; optional later rename with fleet cutover |
| Sonarr `network_mode: host` | Preserve native `localhost` clients during 12.2B | Dual-home + DNS client URLs + Traefik |
| NZBGet `network_mode: container:qbittorrent` | Shared VPN namespace | Independent `hotio` IP **and** equivalent VPN policy |
| Legacy Hive paths (`/hive/jellyfin/tv`, `/hive/downloads`) | Existing libraries | Explicit path migration to `/hive/media/...` |
| Download UIs on host ports (qBittorrent/NZBGet) | Operator convenience / VPN publish | Optional later Traefik or keep internal-only |
| *arr on `hotio` without Traefik yet | Pre-standard deployments | Add `proxy` + routers per this standard |
| `homelab` / other non-core networks | Pre-Phase-12 monitoring/etc. | Out of scope for media standard; do not reuse for *arr |

---

## Rationale

- **Split ingress from automation** so Traefik never needs to sit on the downloader/VPN network, and downloaders never need public exposure  
- **Dual-home *arr + Prowlarr** so one container can serve humans (`proxy`) and talk to clients/indexers (`hotio`) without hairpinning through the host  
- **Docker DNS over localhost** survives container restarts and removes host-network coupling  
- **External named networks** match DockerStandard: networks are host-provided, not redefined per compose project  

---

## Compliance checklist (media migrations)

- [ ] Service attached only to approved networks for its role (`proxy` / `hotio`) per membership table  
- [ ] Dual-homed apps set `traefik.docker.network=proxy`  
- [ ] No new host ports for UIs when Traefik router is active  
- [ ] Download client / indexer host fields use Docker DNS, not `localhost` (unless exception filed)  
- [ ] App state under `/mnt/monarch/appdata/<service>`  
- [ ] Media/downloads remain on Hive; path strategy documented  
- [ ] VPN / shared-netns exceptions explicitly recorded  

---

## References

- Phase 12.1 Traefik pilot — `Documentation/Phase12.1/`  
- Phase 12.2A download clients — `Documentation/Phase12.2A/`  
- Phase 12.2B Sonarr (host-net exception) — `Documentation/Phase12.2B/`  
- Docker compose SoT — `services/<service>/`
