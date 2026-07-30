# jellyseerr

Phase 10.75 repository import of the live deployment.

## Purpose
Media request management for Jellyfin

## Runtime
- Container(s): `jellyseerr`
- Compose: `services/jellyseerr/compose.yaml`
- Former source of truth: CasaOS `breathtaking_ken`

## Important
This import **does not** migrate storage. Bind mounts are unchanged from the live container.

## Operations
```bash
cd services/jellyseerr
cp -n .env.example .env   # if required
docker compose -f compose.yaml config
# Do not recreate unless cutting over from CasaOS/Portainer intentionally
```

## Documentation
See `Documentation/services/jellyseerr/`.
