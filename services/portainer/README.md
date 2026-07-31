# Portainer CE (Phase 12.1 pilot)

## Deploy

```bash
cd services/portainer
docker compose up -d
```

## Storage

`/mnt/monarch/appdata/portainer` → `/data`

## Health

In-container healthcheck **exempt** (distroless). Smoke: `curl -fsS http://127.0.0.1:9000/api/status`

## Exceptions

RW docker.sock; `portainer_network`; healthcheck exemption — see `Documentation/Phase12.1/Known_Exceptions.md`.
