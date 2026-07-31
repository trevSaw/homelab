# Uptime Kuma — Phase 12.1 Validation

## Before

- Compose SoT: CasaOS `/var/lib/casaos/apps/uptimekuma/docker-compose.yml`
- Image: `louislam/uptime-kuma:1.23.10-alpine` (already pinned)
- Storage: `/DATA/AppData/uptimekuma/app/data` (13M)
- Network: `bridge`
- Health: healthy (CasaOS)

See `inspect/before-uptimekuma.json`.

## Steps

1. Stop CasaOS container.
2. `rsync -aHAX` data → `/mnt/monarch/appdata/uptime-kuma`.
3. Remove old container name conflict; start from `services/uptime-kuma`.
4. Attach to external `proxy` network; add healthcheck + memory limit.
5. Rename `/DATA/AppData/uptimekuma/app/data` → `data.old`.

## After

- Compose SoT: `services/uptime-kuma`
- Mount: `/mnt/monarch/appdata/uptime-kuma` → `/app/data`
- Health: **healthy**
- HTTP `:3001` → 302
- Image unchanged pin `1.23.10-alpine`

See `inspect/after-uptimekuma.json`.

## Volume migration

| From | To | Size |
|---|---|---|
| `/DATA/AppData/uptimekuma/app/data` | `/mnt/monarch/appdata/uptime-kuma` | ~13M |

Rollback tree: `/DATA/AppData/uptimekuma/app/data.old`

## Rollback

```bash
docker stop uptimekuma
# restore data.old -> data if needed, point compose volume back, or:
# mv data.old data; start previous CasaOS project
```

## Exceptions

Host port 3001; upstream root user — Known_Exceptions.md.
