# Portainer — Phase 12.1 Validation

## Before

- Compose SoT: already `services/portainer`
- Image: `portainer/portainer-ce:lts` (runtime 2.33.6)
- Storage: `/mnt/monarch/appdata/portainer` (already)
- Healthcheck: broken CMD-SHELL wget (distroless) → unhealthy
- Network: `portainer_network`

See `inspect/before-portainer.json`.

## Steps

1. Pin image to `portainer/portainer-ce:2.33.6`.
2. Remove broken in-container healthcheck; document external smoke.
3. Mark `portainer_network` external; keep RW docker.sock exception.
4. Add `.env.example`, `README.md`, `Versions.md`.
5. `docker compose up -d` from repo.

## After

- Image: `portainer/portainer-ce:2.33.6`
- Status: running
- Smoke: `GET /api/status` → 200, Version 2.33.6
- Storage unchanged on appdata

See `inspect/after-portainer.json`.

## Volume migration

None (already migrated in Phase 11).

## Rollback

```bash
cd services/portainer
# revert compose.yaml from git / Validation backup, then:
docker compose up -d
```

## Exceptions

RW docker.sock; healthcheck exemption; dedicated network — Known_Exceptions.md.
