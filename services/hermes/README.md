---
title: Hermes Service README
document_type: README
service: hermes
owner: Homelab
status: Active
version: 14.1.0
last_reviewed: 2026-08-01
related_documents:
  - Architecture/decisions/ADR-0004-KORA-Orchestration-Hermes.md
  - AI/Hermes/README.md
  - AI/KORA/Config/hermes_registration.yaml
---

# Hermes (Thin Execution Layer)

Orchestration **substrate** only (ADR-0004). Hermes is not KORA.

## Phase 14.1 posture

| Concern | Stage 1 decision |
| --- | --- |
| Primary chat path | **No** — Open WebUI → KORA → Ollama |
| Identity | Must not claim KORA / Brainiac |
| Replacement | **Reworked in place** (same container/data); role narrowed |
| Future | Distributed Council / agent transport (later phases) |

## Phase 14 Hermes migration posture (branch `phase14-hermes-runtime`)

The target architecture moves Hermes back onto the chat path as the generic
runtime entry:

```text
Open WebUI → Hermes (api_server :8642) → KORA (intelligence) → Memory/Knowledge/Tools → Ollama
```

This is an **evaluation + incremental migration**, not a completed cutover.

- **API server platform** is additive config, **default OFF**
  (`API_SERVER_ENABLED=false`) so the current direct KORA path is preserved.
- Enable at cutover via env: `API_SERVER_ENABLED=true`,
  `API_SERVER_KEY=<high-entropy>`, `API_SERVER_MODEL_NAME=KORA`.
- **Hermes → KORA delegation** is configured on the host in
  `/mnt/monarch/appdata/hermes/config.yaml` under `delegation:` (not env):
  `base_url: http://kora:8080/v1`, `api_mode: chat_completions`,
  `api_key: <KORA_HERMES_TOKEN>`.
- KORA identity, governance, Memory policy, Knowledge policy, and
  explainability remain KORA-owned. Hermes provides routing, sessions, agent
  loop, tool/MCP transport, and model plumbing only.
- Design docs: `Documentation/Phase14/Phase14-Migration/`.

## Migration

| Item | Decision |
| --- | --- |
| Prior SoT | `/mnt/monarch/appdata/hermes/compose.yml` |
| Compose SoT now | `services/hermes/compose.yaml` (**live ownership migrated 2026-08-01**) |
| Data | **Preserved** `/mnt/monarch/appdata/hermes` |
| Action | Align live project to repo SoT; thin-layer role retained |
| Legacy appdata compose | Disabled; see appdata `README.COMPOSE_OWNERSHIP.md` |

## Exceptions

| Item | Exception |
| --- | --- |
| Image pin | Upstream still tracked as `:latest` until a stable digest audit |
| Healthcheck | Best-effort against dashboard port; may need adjustment if image entrypoint differs |
