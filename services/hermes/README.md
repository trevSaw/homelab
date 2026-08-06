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
