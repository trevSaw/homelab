# qBittorrent / Hotio (Phase 12.2A)

VPN-backed qBittorrent. Config: `/mnt/monarch/appdata/hotio`. Downloads: `/hive/downloads/completed`.

NZBGet shares this container’s network namespace (`network_mode: container:qbittorrent`). After recreating this stack, recreate NZBGet next.

```bash
cd services/Hotio
cp .env.example .env   # if needed
docker compose up -d
# then: cd ../NZBget && docker compose up -d
```

Do not upgrade to qBittorrent 5.x in this phase.
