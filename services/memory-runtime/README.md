---
title: KORA Memory Runtime Logical Service
document_type: README
service: memory-runtime
owner: KORA
status: RETIRED
version: 14.2A
last_reviewed: 2026-08-11
related_documents:
  - Documentation/Phase14/Phase14-Migration/10-kora-runtime-retirement.md
---

# Memory Runtime (RETIRED)

> **RETIRED 2026-08-11.** The old standalone KORA Runtime — including its
> in-process Memory Runtime and Approval Engine — is retired. KORA is now a
> Hermes Agent and uses the **Hermes native Honcho memory provider**
> (workspace `kora`, peer `user`). The historical implementation is preserved
> in Git history and the production backup.

## Historical (pre-retirement)

Event-driven, ephemeral Memory proposal lifecycle for KORA, co-located in the
KORA process (`AI/KORA/Runtime/app/memory_runtime.py`). Approval Engine owned
state transitions; Honcho was the future durable store.
