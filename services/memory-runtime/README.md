---
title: KORA Memory Runtime Logical Service
document_type: README
service: memory-runtime
owner: KORA
status: Foundation
version: 14.2A
last_reviewed: 2026-08-03
related_documents:
  - Architecture/ai/Memory_Runtime.md
  - Architecture/decisions/ADR-14.2A-001-Internal-Event-Bus.md
  - Documentation/Phase14/Phase14.2A/Memory_Runtime_Architecture.md
  - Validation/Phase14.2A/
---

# Memory Runtime

Event-driven, ephemeral Memory proposal lifecycle for KORA.

## Phase 14.2A deployment

Memory Runtime and Approval Engine are logical services co-located in the KORA
process. They have no standalone containers or durable volumes. Runtime code is
in:

- `AI/KORA/Runtime/app/memory_runtime.py`
- `AI/KORA/Runtime/app/memory_models.py`
- `AI/KORA/Runtime/app/approval_engine.py`

## Responsibilities

- Subscribe to relevant general Event Bus topics.
- Require explicit candidate data; perform no autonomous extraction.
- Normalize and evaluate candidate eligibility.
- Create and track ephemeral proposals.
- Forward eligible proposals to Approval Engine.
- Expose read-only proposal status through KORA.

Approval Engine alone owns state transitions. Memory Runtime owns proposal
lifecycle coordination. Honcho remains disconnected and owns only future
durable persistence.

## Internal interfaces

- Memory Runtime: `create_proposal`, `list_pending`, `get_proposal`
- Approval Engine: `approve`, `reject`, `expire`, `withdraw`

## Prohibited in this phase

No durable writes, Honcho calls, Open WebUI changes, approval UI, MCP ingestion,
Graphify, ChromaDB, embeddings, vector search, event persistence, or replay.
