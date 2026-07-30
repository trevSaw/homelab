# nextcloud

Phase 10.75 repository import of the live deployment.

## Purpose
Nextcloud files + MariaDB

## Runtime
- Container(s): `nextcloud,nextcloud-db`
- Compose: `services/nextcloud/compose.yaml`
- Former source of truth: CasaOS `nextcloud (stale); live uses /hive/cloud`

## Important
This import **does not** migrate storage. Bind mounts are unchanged from the live container.

## Operations
```bash
cd services/nextcloud
cp -n .env.example .env   # if required
docker compose -f compose.yaml config
# Do not recreate unless cutting over from CasaOS/Portainer intentionally
```

## Documentation
See `Documentation/services/nextcloud/`.
