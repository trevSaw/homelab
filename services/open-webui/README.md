---
title: Open WebUI Service README
document_type: README
service: open-webui
owner: Homelab
status: Active
version: 14.1.0
last_reviewed: 2026-08-01
related_documents:
  - Architecture/decisions/ADR-0008-User-Interface-OpenWebUI.md
  - Validation/Phase14.1/Migration_Notes.md
---

# Open WebUI (KORA UI)

UI-only surface for KORA (ADR-0008). Not the product brain.

## Stage 1 path

```text
https://chat.fatherfankscloud.uk
        ↓
   open-webui
        ↓  OPENAI_API_BASE_URL
      kora:8080/v1
        ↓
      ollama
```

## Migration

| Item | Decision |
| --- | --- |
| Prior location | Co-located in `/hive/ollama/compose.yml` |
| New SoT | `services/open-webui/compose.yaml` |
| Data | **Preserved** `/mnt/monarch/appdata/open-webui` |
| Traefik host | Unchanged `chat.fatherfankscloud.uk` |
| Backend | Migrated from direct Ollama → KORA OpenAI façade |

## Deployment

```bash
cd /home/fatherfrank/projects/homelab/services/open-webui
cp -n .env.example .env
# Copy WEBUI_SECRET_KEY from legacy env (do not commit)
docker compose -f compose.yaml config >/dev/null
docker compose -f compose.yaml up -d
```

Requires `kora` healthy on `ollama_ollama-net` before chat works.

## SoT boundaries

Open WebUI data at `/mnt/monarch/appdata/open-webui` is **UI application runtime
data only** (including built-in `vector_db` / embeddings caches). It is **not**
KORA Memory or Knowledge Source of Truth.

See `AI/OpenWebUI/Config/sot_boundaries.yaml` and
`Documentation/Phase14/Phase14.2/Preflight_Assessment.md`.

## Exceptions

| Item | Exception |
| --- | --- |
| Built-in RAG / memory | Must remain unused for KORA SoT paths (architecture) |
| Cert resolver label | Uses `le` to match Phase 12 Traefik stacks (legacy used `letsencrypt`) |
