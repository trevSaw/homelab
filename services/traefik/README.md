# Traefik — reverse proxy (Phase 12.1 pilot)

## Overview

Edge reverse proxy for the homelab. TLS via Cloudflare DNS challenge; Docker provider on network `proxy`.

## Deploy

```bash
cd services/traefik
cp .env.example .env   # fill secrets
docker compose up -d
```

## Required env

See `.env.example`.

## Storage

| Host path | Container | Notes |
|---|---|---|
| `/mnt/monarch/appdata/traefik/acme.json` | `/etc/traefik/acme.json` | ACME cert store (mode 600) |

## Exceptions

See `Documentation/Phase12.1/Known_Exceptions.md` — host ports 80/443, docker.sock `:ro`, official image user.

## Rollback

```bash
cd /hive/traefik && docker compose up -d
# or restore services/traefik/compose.yaml from Validation/Phase12.1/traefik/
```
