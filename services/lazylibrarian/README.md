# lazylibrarian

Phase 10.75 repository import of the live deployment.

## Purpose
Ebook/audiobook automation

## Runtime
- Container(s): `linuxserver-lazylibrarian-app-1`
- Compose: `services/lazylibrarian/compose.yaml`
- Former source of truth: CasaOS `linuxserver-lazylibrarian`

## Important
This import **does not** migrate storage. Bind mounts are unchanged from the live container.

## Operations
```bash
cd services/lazylibrarian
cp -n .env.example .env   # if required
docker compose -f compose.yaml config
# Do not recreate unless cutting over from CasaOS/Portainer intentionally
```

## Documentation
See `Documentation/services/lazylibrarian/`.
