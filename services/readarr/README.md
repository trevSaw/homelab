# readarr

Phase 10.75 repository import of the live deployment.

## Purpose
Book manager (Readarr develop)

## Runtime
- Container(s): `readarr`
- Compose: `services/readarr/compose.yaml`
- Former source of truth: Portainer/hive compose (see Diff.md)

## Important
This import **does not** migrate storage. Bind mounts are unchanged from the live container.

## Operations
```bash
cd services/readarr
cp -n .env.example .env   # if required
docker compose -f compose.yaml config
# Do not recreate unless cutting over from CasaOS/Portainer intentionally
```

## Documentation
See `Documentation/services/readarr/`.
