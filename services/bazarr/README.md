# bazarr

Phase 10.75 repository import of the live deployment.

## Purpose
Subtitle companion for Sonarr/Radarr

## Runtime
- Container(s): `bazarr`
- Compose: `services/bazarr/compose.yaml`
- Former source of truth: CasaOS `bazarr`

## Important
This import **does not** migrate storage. Bind mounts are unchanged from the live container.

## Operations
```bash
cd services/bazarr
cp -n .env.example .env   # if required
docker compose -f compose.yaml config
# Do not recreate unless cutting over from CasaOS/Portainer intentionally
```

## Documentation
See `Documentation/services/bazarr/`.
