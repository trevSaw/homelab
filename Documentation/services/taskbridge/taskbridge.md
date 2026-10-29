> **DEPRECATED (Phase 22) — pending removal.** See ADR-0011 / `Documentation/Phase22/KORA_OpenCode_Go_Migration.md`.

---
title: Task Bridge — Service Documentation
document_type: service
service: taskbridge
owner: Homelab
status: Active
version: 1.0.0
last_reviewed: 2026-09-23
related_documents:
  - services/taskbridge/README.md
  - Architecture/decisions/ADR-0010-KORA-Execution-Worker-OpenCode-Task-Bridge.md
  - Documentation/Phase20/KORA_OpenCode_Worker.md
---

# Task Bridge

Containerized execution bridge that lets **KORA** (Hermes) delegate engineering
and troubleshooting tasks to **OpenCode** running as a detached worker against
the canonical homelab repository, with governed execution boundaries and
approval gating.

- Architecture & operations: `Documentation/Phase20/KORA_OpenCode_Worker.md`
- Service runbook: `services/taskbridge/README.md`
- Decision record: `ADR-0010`
- Compose: `services/taskbridge/compose.yaml`

Quick facts:

- Network: `proxy` + `ollama-net` (internal only, no published ports).
- Auth: bearer token on REST + MCP endpoints.
- Boundaries: `read_only` / `test_write` (isolated worktree) /
  `production_write` (approval-gated).
- Worker: OpenCode 1.18.32 on `gpt-oss:20b-cloud` via Ollama.
- Persistence: SQLite under `/mnt/monarch/appdata/taskbridge/`.