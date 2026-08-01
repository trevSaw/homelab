---
title: Home Assistant Deployment Evidence
document_type: Audit
service: homeassistant
owner: Homelab
status: Active
version: 1.0.0
last_reviewed: 2026-07-31
---

# Deployment Evidence — Home Assistant (Phase 12)

Host: mocha. Date: 2026-07-31. Image: `ghcr.io/home-assistant/home-assistant:2026.7.4`.

## Result

**PASS WITH DOCUMENTED EXCEPTIONS** — container healthy, Traefik ingress working,
storage confined to `/mnt/monarch/appdata/homeassistant`, no published host ports.

## Platform preconditions verified

| Check | Observed |
|---|---|
| `proxy` network | exists, subnet `172.19.0.0/16` |
| Traefik | `traefik:v3.6.7`, Up (healthy), on `proxy`, `:80`/`:443` |
| Traefik entrypoints | `web` (redirects to `websecure`), `websecure` |
| Traefik cert resolver | `le` (Cloudflare DNS-01) |
| Traefik discovery | `providers.docker.exposedbydefault=false` → `traefik.enable=true` required |
| DNS | `homeassistant.fatherfankscloud.uk` → `192.168.50.44` (host) |

## Runtime verification

```text
docker compose ps                → homeassistant Up (healthy)
docker inspect networks          → proxy only
docker port homeassistant        → (empty, no published ports)
in-container curl :8123          → 302
curl -H Host: … http://127.0.0.1 → 301 → https://homeassistant.fatherfankscloud.uk/
curl https://homeassistant.…/    → 302
curl -L https://homeassistant.…/ → 200  https://homeassistant.fatherfankscloud.uk/onboarding.html
TLS certificate                  → CN=fatherfankscloud.uk, Let's Encrypt, valid to 2026-10-18
```

## Incidents encountered and resolved

### 1. Traefik `404 page not found`

Cause: the labelled container had not been started, so with
`exposedbydefault=false` Traefik had no router for the host. Resolution: deploy
the stack. This is the expected Traefik response for an unmatched Host rule.

### 2. Restart loop, exit code 126

```text
/package/admin/s6-overlay/libexec/stage0: exec: line 83: /run/s6/basedir/bin/init: Permission denied
```

Cause: Docker mounts `tmpfs` with `noexec` by default; the image's s6-overlay
init runs executables from `/run`. Resolution: `/run:mode=0755,size=64m,exec` in
`compose.yaml`. `/tmp` retains the default hardened options.

### 3. HTTP 400 via Traefik

```text
ERROR [homeassistant.components.http.forwarded] A request from a reverse proxy
was received from 172.19.0.2, but your HTTP integration is not set-up for reverse proxies
```

Cause: missing reverse-proxy trust. Resolution: `/config/configuration.yaml` now
contains:

```yaml
http:
  use_x_forwarded_for: true
  trusted_proxies:
    - 172.19.0.0/16
    - 127.0.0.1
    - ::1
```

Pre-change file backed up to `/tmp/ha-configuration.yaml.bak` at change time;
the authoritative template is `services/homeassistant/config/configuration.yaml.example`.

## Outstanding items for operator

- [ ] Complete Home Assistant onboarding (create owner account) at `https://homeassistant.fatherfankscloud.uk`
- [ ] Take first backup per `services/homeassistant/README.md` after onboarding
- [ ] Re-confirm `trusted_proxies` if the `proxy` network is ever recreated with a different subnet
