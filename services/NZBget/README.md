# NZBGet (Phase 12.2A)

Usenet client. Config: `/mnt/monarch/appdata/nzbget`. Downloads: `/hive/downloads`.

Requires running `qbittorrent` first (`network_mode: container:qbittorrent`).

```bash
cd services/Hotio && docker compose up -d
cd ../NZBget
cp .env.example .env   # if needed
docker compose up -d
```

WebUI is on the host via Hotio’s published port `:6789`.
