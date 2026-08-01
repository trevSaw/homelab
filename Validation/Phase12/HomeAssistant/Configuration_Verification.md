---
title: Home Assistant Configuration Verification
document_type: Audit
service: homeassistant
owner: Homelab
status: Active
version: 1.0.0
last_reviewed: 2026-07-31
---

# Configuration Verification — Home Assistant (Phase 12)

## Compose / environment

| Check | Expected | Pass? |
|---|---|---|
| Compose file name | `compose.yaml` | [ ] |
| No `version:` key | Absent | [ ] |
| Image | `ghcr.io/home-assistant/home-assistant:2026.7.4` (or newer **pinned** tag recorded in Versions.md) | [ ] |
| `container_name` / `hostname` | `homeassistant` | [ ] |
| `restart` | `unless-stopped` | [ ] |
| `env_file` | `.env` | [ ] |
| `TZ` sourced from env | Matches host policy | [ ] |
| Volume | `/mnt/monarch/appdata/homeassistant:/config` only | [ ] |
| `tmpfs` | `/tmp`, `/run` | [ ] |
| Networks | `proxy` external only | [ ] |
| `ports` | omitted | [ ] |
| `privileged` | absent / false | [ ] |
| `security_opt` | `no-new-privileges:true` | [ ] |
| Traefik Host | `homeassistant.fatherfankscloud.uk` | [ ] |
| LB port | `8123` | [ ] |
| Healthcheck | curl to `127.0.0.1:8123` | [ ] |
| Logging | `10m` / `5` | [ ] |
| Limits | `cpus: "2.0"`, `memory: 2G` | [ ] |

## Live `/config` (appdata)

| Check | Expected | Pass? |
|---|---|---|
| Path exists | `/mnt/monarch/appdata/homeassistant` | [ ] |
| `configuration.yaml` present after first boot | yes | [ ] |
| `http.use_x_forwarded_for` | `true` | [ ] |
| `http.trusted_proxies` includes proxy CIDR | e.g. `172.19.0.0/16` from `docker network inspect proxy` | [ ] |
| No recorder/DB path outside appdata | confirmed | [ ] |
| Secrets / tokens not copied into git | confirmed | [ ] |

## Network / Traefik live

```bash
PROXY_SUBNET=$(docker network inspect proxy --format '{{range .IPAM.Config}}{{.Subnet}}{{end}}')
echo "proxy subnet=$PROXY_SUBNET"
docker inspect homeassistant --format '{{json .NetworkSettings.Networks}}'
docker exec homeassistant curl -fsS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8123/
curl -fsSI https://homeassistant.fatherfankscloud.uk/ | head -n 15
```

| Check | Expected | Pass? |
|---|---|---|
| Proxy subnet documented in HA trusted_proxies | match | [ ] |
| Only `proxy` network key in inspect | yes | [ ] |
| HTTP 200/302 from Traefik | yes | [ ] |

## Cross-check documentation

| Artifact | Present | Pass? |
|---|---|---|
| `service.md` / `service.json` | [ ] | [ ] |
| ADR-0003 | [ ] | [ ] |
| Deployment / Validation / Rollback docs | [ ] | [ ] |
| Implementation_Notes.md | [ ] | [ ] |

**Verified by:** ________________ **Date:** ________________
