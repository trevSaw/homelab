# sparkyfitness

## Overview
- Purpose: Self-hosted fitness/health tracker (nutrition, exercise, sleep, hydration, mood, fasting)
- Category: Productivity
- Current lifecycle state: Production (deployed 2026-08-15)
- Importance level: Operational

## Repository Location
- Service directory: `services/sparkyfitness/`
- Compose file: `services/sparkyfitness/compose.yaml`
- Documentation path: `Documentation/services/sparkyfitness/sparkyfitness.md`

## Runtime Information
- Container names: sparkyfitness-db, sparkyfitness-server, sparkyfitness-frontend
- Restart policy: unless-stopped
- Environment files: `.env` (gitignored, secrets), `.env.example` (template)
- Networks: `proxy` (external, Traefik ingress on frontend), `sparkyfitness` (internal), `ollama-net` (external, on server only)
- Volumes: `/mnt/monarch/appdata/sparkyfitness/{postgresql,backup,uploads}`

## Local AI (Ollama)
- Server is attached to the external `ollama-net` network; reaches Ollama at `http://ollama:11434` (OpenAI-compatible endpoint at `/v1`, no API key required).
- Global AI service pre-provisioned in `ai_service_settings`: `service_type=ollama`, `custom_url=http://ollama:11434`, `model_name=gemma3:4b`, `chat_tool_profile=core`, public.
- `ALLOW_PRIVATE_NETWORK_AI=true` allows non-admin users to use private/local AI URLs.
- Shared Ollama runs `OLLAMA_CONTEXT_LENGTH=16384` (see `services/ollama/`).

### Ollama `custom_url` gotcha
For `service_type=ollama` the app derives the base URL as `${custom_url}/v1`
(`SparkyFitnessServer/ai/config.ts` → `getOpenAiCompatibleBaseUrl`), then the
AI SDK appends `/chat/completions`. **Do not include `/v1` in `custom_url`.**
- Correct: `http://ollama:11434` → `http://ollama:11434/v1/chat/completions`
- Wrong: `http://ollama:11434/v1` → `http://ollama:11434/v1/v1/chat/completions` (404)

## Architecture Relationships
- Upstream dependencies: PostgreSQL 18
- Downstream consumers: web frontend (nginx) proxying `/api` to the server
- Reverse proxy relationships: Traefik routes `sparkyfitness.fatherfankscloud.uk` -> frontend :80

## Security Review
- Secret handling approach: secrets in gitignored `.env`; generated with `openssl rand`
- Privileged mode status: not used
- Docker socket exposure: none
- External exposure: none — internal homelab only (no public Cloudflare DNS records)
- Known risks: default signup enabled; review/disable after initial account creation

## Operational Notes
- Backup considerations: appdata directory covered by host backup; app writes its own backups to `/mnt/monarch/appdata/sparkyfitness/backup`
- Recovery notes: see runbooks
- Monitoring requirements: container healthchecks; Traefik router health
- Maintenance considerations: pin image tags (see `Versions.md`); review upstream release notes before upgrading

## Governance Metadata
- ADR references: []
- Migration priority: N/A (new deployment)
- Migration wave: N/A

### Evidence References

Classification:
- Source: Upstream repository release v1.6.2
- Service: sparkyfitness

Runtime:
- Deployed 2026-08-15, verified healthy.

Dependencies:
- Source: upstream docker/docker-compose.prod.yml

Risks:
- Source: Deployment plan 2026-08-15
- Risk: Internal DNS record pending in Pi-hole (sparkyfitness.fatherfankscloud.uk -> 192.168.50.44)

Migration:
- Source: N/A

ADRs:
- None identified.

## Known Issues
- `sparkyfitness.fatherfankscloud.uk` currently resolves to the blackhole `0.0.0.9` from the
  homelab Pi-hole (192.168.50.213) until an A record is added by the administrator.
- AI test "Failure: The AI service returned an error... 404 page not found" ⇒
  `custom_url` in `ai_service_settings` contains a `/v1` suffix (see Local AI gotcha above).
