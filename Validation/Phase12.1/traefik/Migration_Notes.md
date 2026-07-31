# Traefik — Phase 12.1 Validation

## Before

- Compose SoT: `/hive/traefik/compose.yaml`
- Image: `traefik:latest` (runtime 3.6.7)
- Storage: `/mnt/monarch/appdata/traefik/acme.json` (already)
- docker.sock: RW on hive compose; repo already `:ro`
- Restart: `always`
- Healthcheck: none on live hive compose

See `inspect/before-traefik.json`.

## Steps

1. Wrote standardized `services/traefik/compose.yaml` (pin `traefik:v3.6.7`, healthcheck, resources, INFO logs, sock `:ro`).
2. Created `.env.example`, `README.md`, `Versions.md`.
3. Replaced accidental symlink `services/traefik/.env -> ../.env` with a **dedicated** traefik `.env` (restored shared `services/.env` from live Authentik/hive values — see Completion Report lesson).
4. `docker compose up -d --force-recreate` from `services/traefik`.
5. Backed up hive compose to `/hive/traefik/compose.yaml.phase12.1.bak`.

## After

- Compose SoT: `services/traefik`
- Image: `traefik:v3.6.7`
- Health: **healthy**
- ACME mount unchanged on appdata
- `docker compose config`: OK
- `traefik healthcheck --ping`: OK

See `inspect/after-traefik.json`.

## Volume migration

None required (ACME already on appdata). Documented only.

## Rollback

```bash
cd /hive/traefik && docker compose up -d
# or: cp compose.yaml.phase12.1.bak compose.yaml
```

## Exceptions

Host ports 80/443; docker.sock `:ro`; official image user — see Known_Exceptions.md.
