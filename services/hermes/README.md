---
title: Hermes Service README
document_type: README
service: hermes
owner: Homelab
status: Active
version: 14.1.0
last_reviewed: 2026-08-11
related_documents:
  - Architecture/decisions/ADR-0004-KORA-Orchestration-Hermes.md
  - AI/Hermes/README.md
  - AI/KORA/Config/hermes_registration.yaml
  - Documentation/Phase14/Phase14-Migration/10-kora-runtime-retirement.md
---

# Hermes (KORA runtime platform)

Hermes is the **generic agent/runtime platform**. KORA is a **Hermes Agent**
(head intelligence/governance agent) hosted inside it. There is **no standalone
KORA Runtime**; the old standalone runtime was retired 2026-08-11.

## Final architecture (Phase 14 closeout)

```text
Open WebUI → Hermes (api_server :8642, model "KORA") → KORA HEAD AGENT
                                                       ├── Honcho (native provider)
                                                       ├── Chroma
                                                       ├── Graphify
                                                       ├── Ollama (model.default)
                                                       └── MCP / Tools (Hermes tool runtime)
```

| Concern | Final decision |
| --- | --- |
| Runtime | Hermes v0.17.0 (api_server platform) |
| KORA | Hermes Agent — plugin at `/opt/data/plugins/kora` |
| Primary chat path | **Yes** — Open WebUI → Hermes → KORA → Ollama |
| Model | Controlled by Hermes `config.yaml model.default` (currently `qwen3:8b`) |
| Memory | Hermes native honcho provider (workspace `kora`, peer `user`) |
| KORA identity | Presented as **KORA** (API_SERVER_MODEL_NAME=KORA) |

## Notes

- KORA identity, governance, Memory policy, Knowledge policy, and
  explainability are KORA-owned; Hermes provides routing, sessions, agent
  loop, tool/MCP transport, and model plumbing.
- Historical Phase 14.1 "thin execution layer" posture and the delegation
  design (`delegation: base_url: http://kora:8080/v1`) are superseded by the
  retirement of the standalone KORA Runtime.
- Design/migration docs: `Documentation/Phase14/Phase14-Migration/`.

## Migration

| Item | Decision |
| --- | --- |
| Prior SoT | `/mnt/monarch/appdata/hermes/compose.yml` |
| Compose SoT now | `services/hermes/compose.yaml` (**live ownership migrated 2026-08-01**) |
| Data | **Preserved** `/mnt/monarch/appdata/hermes` |
| Legacy appdata compose | Disabled; see appdata `README.COMPOSE_OWNERSHIP.md` |

## Exceptions

| Item | Exception |
| --- | --- |
| Image pin | Pinned to Hermes Agent v0.17.0 digest (see compose) |
| Healthcheck | Best-effort against api_server `/health` (`:8642`) |
