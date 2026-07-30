# prowlarr

Phase 10.75 repository import of the live deployment.

## Purpose
Indexer manager for *arr stack

## Runtime
- Container(s): `prowlarr`
- Compose: `services/prowlarr/compose.yaml`
- Former source of truth: CasaOS `glorious_thomas`

## Important
This import **does not** migrate storage. Bind mounts are unchanged from the live container.

## Operations
```bash
cd services/prowlarr
cp -n .env.example .env   # if required
docker compose -f compose.yaml config
# Do not recreate unless cutting over from CasaOS/Portainer intentionally
```

## Documentation
See `Documentation/services/prowlarr/`.
