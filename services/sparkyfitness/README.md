---
title: SparkyFitness Service README
document_type: README
service: sparkyfitness
owner: Homelab
status: Active
version: 1.0.0
last_reviewed: 2026-08-15
related_documents:
  - Documentation/services/sparkyfitness/sparkyfitness.md
---

# SparkyFitness

Self-hosted, privacy-first fitness and health tracking platform (a MyFitnessPal
alternative). Tracks nutrition, exercise, body metrics, sleep, hydration, mood,
and fasting. Provides a web frontend, an API backend, and optional native mobile
apps.

## Deployment

```bash
cd services/sparkyfitness
docker compose up -d
```

Access at `https://sparkyfitness.fatherfankscloud.uk` (internal, via Traefik).

## Topology

```text
Traefik (proxy network)
  └── sparkyfitness-frontend (nginx, :80)
        └── sparkyfitness-server (:3010)
              └── sparkyfitness-db (postgres :5432)
```

- `frontend` is attached to `proxy` (Traefik ingress) and `sparkyfitness`.
- `server` and `db` are on the internal `sparkyfitness` network only — the
  database is not reachable outside the compose project.
- No host ports are published; Traefik is the sole ingress.

## Notes

- Images are pinned to release `v1.6.2` (see `Versions.md`). Do not switch to
  `:latest`; upstream warns against auto-updating.
- Garmin microservice is intentionally not deployed (WIP upstream).
- First login: register with `SPARKY_FITNESS_ADMIN_EMAIL` in `.env`
  (`tsawyerm@gmail.com`) to get the admin role.
- `.env` holds secrets and is gitignored; use `.env.example` as a template.

## Local AI (Ollama)

- The `server` container is attached to the external `ollama-net`
  (`ollama_ollama-net`) so it can reach Ollama at `http://ollama:11434`
  (OpenAI-compatible endpoint at `/v1`; no API key required).
- A global "Local Ollama" AI service is pre-provisioned in `ai_service_settings`:
  `service_type=ollama`, `custom_url=http://ollama:11434`,
  `model_name=gemma3:4b`, `chat_tool_profile=core`, public to all users.
- `ALLOW_PRIVATE_NETWORK_AI=true` lets non-admin users use private/local AI URLs.
- The shared Ollama server runs `OLLAMA_CONTEXT_LENGTH=16384`
  (`services/ollama/`) per the SparkyFitness docs; raising it prevents truncated
  tool calls on the chatbot. This affects all Ollama consumers (KORA/Hermes,
  Honcho, code-server, Odysseus).

### Ollama `custom_url` gotcha (read before editing AI services)

For `service_type=ollama`, SparkyFitness **derives** the base URL as
`${custom_url}/v1` (see `SparkyFitnessServer/ai/config.ts` →
`getOpenAiCompatibleBaseUrl`), then the AI SDK appends `/chat/completions`.

**Therefore `custom_url` must NOT include a `/v1` suffix.**

- Correct: `custom_url = http://ollama:11434` → base `http://ollama:11434/v1`
  → request `http://ollama:11434/v1/chat/completions` (works).
- Wrong: `custom_url = http://ollama:11434/v1` → base
  `http://ollama:11434/v1/v1` → request `.../v1/v1/chat/completions`
  (returns `404 page not found`, "Check the API key, model name, and URL").

Affected if editing AI service settings in the web UI: store the bare host, not
the `/v1` endpoint.

## Exceptions

| Item | Exception |
| --- | --- |
| Internal DNS | `sparkyfitness.fatherfankscloud.uk` requires an A record (-> 192.168.50.44) in the homelab Pi-hole; record must be added for LAN resolution. |
