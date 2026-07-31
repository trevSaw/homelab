# Beszel hub (Phase 12.1 pilot)

Monitoring hub. Data: `/mnt/monarch/appdata/beszel/beszel_data`.

```bash
cd services/beszel
cp .env.example .env
docker compose up -d
```

Agent is separate: `services/beszel_agent/`.
