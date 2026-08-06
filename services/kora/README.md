---
title: KORA Runtime Service README
document_type: README
service: kora
owner: Homelab
status: Active
version: 14.2A
last_reviewed: 2026-08-03
related_documents:
  - Architecture/ai/Production_Architecture.md
  - Architecture/ai/Rollout_Strategy.md
  - Architecture/decisions/ADR-0004-KORA-Orchestration-Hermes.md
  - Architecture/decisions/ADR-0008-User-Interface-OpenWebUI.md
  - Architecture/decisions/ADR-14.2A-001-Internal-Event-Bus.md
  - Validation/Phase14.2A/
---

# KORA Runtime (Solo + Phase 14.2A foundation)

## Overview

KORA Solo conductor façade. OpenAI-compatible API on port 8080 (internal).

```text
Open WebUI → http://kora:8080/v1 → Ollama
```

## Architecture

- Product identity: **KORA** (Brainiac)
- Hermes is thin/optional and not on the primary Stage 1 chat path
- Event Bus / Memory proposals: in-process, ephemeral logical services
- Memory retrieval / durable writes / Knowledge / Tools: disabled

## Required external resources

| Resource | Requirement |
| --- | --- |
| Docker network `ollama_ollama-net` | External; shared with Ollama / Hermes / Honcho |
| Docker network `proxy` | External (reserved; Traefik disabled on KORA in Stage 1) |
| Bind path `/mnt/monarch/appdata/kora` | Runtime data directory |
| Healthy `ollama` container | Inference backend |

## Deployment

```bash
sudo mkdir -p /mnt/monarch/appdata/kora
cd /home/fatherfrank/projects/homelab/services/kora
cp -n .env.example .env
docker compose -f compose.yaml config >/dev/null
docker compose -f compose.yaml up -d --build
```

Startup order: **ollama → kora → (hermes optional) → open-webui**.

## Health

```bash
docker exec kora python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8080/health').read().decode())"
```

## Exceptions

| Item | Exception |
| --- | --- |
| Cross-project depends_on | Omitted — Ollama is a separate compose project; order is operational |
| Traefik | Disabled — UI ingress remains on Open WebUI only |
