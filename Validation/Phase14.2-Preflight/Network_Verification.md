# Network Verification — Phase 14.2 Preflight

**Network:** `ollama_ollama-net`  
**Rule:** Must not be deleted.

Post-migration attached containers (2026-08-01):

- ollama
- kora
- open-webui
- hermes
- honcho-api, honcho-deriver, honcho-postgres, honcho-redis
- code-server
- odysseus-odysseus-1

`services/ollama/compose.yaml` declares the network as **external**, so future `docker compose down` in that project will not remove it.
