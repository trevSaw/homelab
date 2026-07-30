# radarr

Phase 10.75 repository import of the live deployment.

## Purpose
Movie collection manager

## Runtime
- Container(s): `radarr`
- Compose: `services/radarr/compose.yaml`
- Former source of truth: CasaOS `radarr`

## Important
This import **does not** migrate storage. Bind mounts are unchanged from the live container.

## Operations
```bash
cd services/radarr
cp -n .env.example .env   # if required
docker compose -f compose.yaml config
# Do not recreate unless cutting over from CasaOS/Portainer intentionally
```

## Documentation
See `Documentation/services/radarr/`.
