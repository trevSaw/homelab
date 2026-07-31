# Beszel agent (Phase 12.1 pilot)

```bash
cd services/beszel_agent
cp .env.example .env   # set KEY + TOKEN from hub
docker compose up -d
```

Secrets must live in `.env` only — never in compose.
