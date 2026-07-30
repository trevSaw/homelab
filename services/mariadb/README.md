# mariadb

Phase 10.75 repository import of the live deployment.

## Purpose
LinuxServer MariaDB (GameIndex)

## Runtime
- Container(s): `linuxserver-mariadb-app-1`
- Compose: `services/mariadb/compose.yaml`
- Former source of truth: CasaOS `linuxserver-mariadb`

## Important
This import **does not** migrate storage. Bind mounts are unchanged from the live container.

## Operations
```bash
cd services/mariadb
cp -n .env.example .env   # if required
docker compose -f compose.yaml config
# Do not recreate unless cutting over from CasaOS/Portainer intentionally
```

## Documentation
See `Documentation/services/mariadb/`.
