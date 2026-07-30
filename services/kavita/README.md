# kavita

Phase 10.75 repository import of the live deployment.

## Purpose
Comics/manga/ebook library

## Runtime
- Container(s): `kavita`
- Compose: `services/kavita/compose.yaml`
- Former source of truth: CasaOS `kavita (stale; live uses /hive/library/Kavita)`

## Important
This import **does not** migrate storage. Bind mounts are unchanged from the live container.

## Operations
```bash
cd services/kavita
cp -n .env.example .env   # if required
docker compose -f compose.yaml config
# Do not recreate unless cutting over from CasaOS/Portainer intentionally
```

## Documentation
See `Documentation/services/kavita/`.
