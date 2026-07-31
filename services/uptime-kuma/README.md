# Uptime Kuma (Phase 12.1 pilot)

## Storage migration

| Before | After |
|---|---|
| `/DATA/AppData/uptimekuma/app/data` | `/mnt/monarch/appdata/uptime-kuma` |

## Deploy

```bash
cd services/uptime-kuma
docker compose up -d
```

Previously CasaOS-managed (`/var/lib/casaos/apps/uptimekuma`).
