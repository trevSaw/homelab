# uptime-kuma

Phase 10.75 repository import of the live deployment.

## Purpose
Uptime Kuma monitoring

## Runtime
- Container(s): `uptimekuma`
- Compose: `services/uptime-kuma/compose.yaml`
- Former source of truth: CasaOS `uptimekuma`

## Important
This import **does not** migrate storage. Bind mounts are unchanged from the live container.

## Operations
```bash
cd services/uptime-kuma
cp -n .env.example .env   # if required
docker compose -f compose.yaml config
# Do not recreate unless cutting over from CasaOS/Portainer intentionally
```

## Documentation
See `Documentation/services/uptime-kuma/`.
