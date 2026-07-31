# Phase 12.1 Known Exceptions

Exceptions discovered/confirmed during the Production Docker Standardization Pilot.

| Service | Exception | Reason | Risk | Mitigation |
|---|---|---|---|---|
| Traefik | Host ports `80`/`443` published | Edge reverse proxy must bind public ports | Medium | Only Traefik publishes these; dashboard behind TLS + Host rule |
| Traefik | Docker socket mounted | Docker provider requires socket | High | Mount **read-only**; `exposedbydefault=false` |
| Traefik | Runs as image default user (root in official image) | Official Traefik image expectation for binding :80/:443 | Medium | Accept until rootless edge design; keep capabilities minimal |
| Portainer | Docker socket **read-write** | Portainer manages containers/stacks | High | Restrict UI access; no public Traefik route without auth |
| Portainer | Healthcheck exemption | Distroless image — no shell/`wget`/`curl` for CMD-SHELL probes | Low | External smoke: `GET /api/status` |
| Portainer | Dedicated `portainer_network` | Existing live network; not `proxy`/`internal` | Low | Documented; future optional attach to `proxy` |
| Beszel | Uses external network `homelab` | Pre-existing monitoring network on host | Low | Documented; optional later move to `internal`/`proxy` |
| Beszel | Host port `8090` | Local hub UI (APP_URL=http://mocha:8090) | Low | LAN-only; no Traefik labels in pilot |
| Beszel-agent | `network_mode: host` | Agent design for host metrics | Medium | Documented; socket `:ro` |
| Beszel-agent | Docker socket mounted | Container inventory | High | Mount **read-only** |
| Uptime Kuma | Host port `3001` | Existing CasaOS exposure | Low | Keep during pilot; Traefik later |
| Uptime Kuma | Container runs as root in upstream image | Upstream default | Medium | Accept; data dir permissions preserved on migrate |
| Layout | Compose lives under `services/` not `compose/<domain>/` | Phase 11 production SoT; domain tree is future layout work | Low | Pilot freezes `services/` as canonical for now |

## Non-exceptions (required practice)

- No secrets in git-tracked compose  
- App state under `/mnt/monarch/appdata/<service>`  
- Images pinned to concrete tags  
- `restart: unless-stopped`  
- Resource memory limits set  
