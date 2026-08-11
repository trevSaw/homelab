---
title: KORA Runtime Service README
document_type: README
service: kora
owner: Homelab
status: RETIRED
version: 14.2A
last_reviewed: 2026-08-11
related_documents:
  - Documentation/Phase14/Phase14-Migration/10-kora-runtime-retirement.md
---

# KORA Runtime (RETIRED)

> **RETIRED 2026-08-11.** The standalone KORA Runtime is no longer part of the
> active architecture. KORA is now a **Hermes Agent** hosted inside Hermes.
>
> - Active chat path: `Open WebUI → Hermes (api_server :8642) → KORA → Ollama`
> - Memory: Hermes native Honcho provider (workspace `kora`, peer `user`)
> - The container `kora` has been removed from active deployment.
> - This compose, the runtime image `homelab/kora-runtime:14.5.0`, and the data
>   at `/mnt/monarch/appdata/kora` are **preserved for rollback/recovery**.
> - Do NOT `docker compose up` this project unless explicitly restoring the old
>   runtime.

## Historical (pre-retirement)

KORA Solo conductor façade. OpenAI-compatible API on port 8080 (internal).

```text
Open WebUI → http://kora:8080/v1 → Ollama
```

- Product identity: **KORA** (Brainiac)
- Event Bus / Memory proposals: in-process, ephemeral logical services
- Requires external networks `ollama_ollama-net` + `proxy`, bind path
  `/mnt/monarch/appdata/kora`, healthy `ollama`
- Traefik disabled in Stage 1 (UI ingress remained on Open WebUI only)
