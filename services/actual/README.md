# actual

Phase 10.75 repository import of the live deployment.

## Purpose
Actual Budget (local-first budgeting)

## Runtime
- Container(s): `actual-server`
- Compose: `services/actual/compose.yaml`
- Former source of truth: CasaOS `big-bear-actual-server`

## Important
This import **does not** migrate storage. Bind mounts are unchanged from the live container.

## Operations
```bash
cd services/actual
cp -n .env.example .env   # if required
docker compose -f compose.yaml config
# Do not recreate unless cutting over from CasaOS/Portainer intentionally
```

## Documentation
See `Documentation/services/actual/`.
