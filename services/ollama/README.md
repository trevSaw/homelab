---
title: Ollama Service README
document_type: README
service: ollama
owner: Homelab
status: Active
version: 14.1.0
last_reviewed: 2026-08-01
related_documents:
  - Validation/Phase14.1/Migration_Notes.md
  - Architecture/ai/Production_Service_Topology.md
---

# Ollama (Inference)

Local LLM inference for KORA Stage 1. Product identity remains **KORA**, not Ollama.

## Migration (Phase 14.1 → 14.2 preflight)

| Item | Decision |
| --- | --- |
| Prior live project | `/hive/ollama/compose.yml` (ollama + open-webui) |
| Compose SoT now | `services/ollama/compose.yaml` (**live ownership migrated 2026-08-01**) |
| Models volume | **Preserved** `/hive/ollama:/root/.ollama` |
| Network | `ollama_ollama-net` marked **external** — do not delete |
| Open WebUI | Split to `services/open-webui` → routes via KORA |
| Legacy hive compose | Disabled; see `/hive/ollama/README.COMPOSE_OWNERSHIP.md` |

## Deployment

```bash
cd /home/fatherfrank/projects/homelab/services/ollama
cp -n .env.example .env
# Copy OLLAMA_API_KEY from legacy /hive/ollama/.env (do not commit)
docker compose -f compose.yaml config >/dev/null
docker compose -f compose.yaml up -d
```

Do **not** `compose down` the legacy project without first confirming dependents
(Hermes, Honcho, code-server, Odysseus) remain attached to `ollama_ollama-net`.

## Exceptions

| Item | Exception |
| --- | --- |
| GPU reservation | NVIDIA device reservation required for local acceleration |
| `CUDA_VISIBLE_DEVICES=-1` | Legacy tuning retained; GPU still reserved via deploy.resources |
| Image pin | Prefer pinned tag in `Versions.md`; `latest` was legacy |
