---
title: KORA Event Bus Logical Service
document_type: README
service: event-bus
owner: KORA
status: RETIRED
version: 14.2A
last_reviewed: 2026-08-11
related_documents:
  - Documentation/Phase14/Phase14-Migration/10-kora-runtime-retirement.md
---

# Event Bus (RETIRED)

> **RETIRED 2026-08-11.** The old standalone KORA Runtime — including its
> in-process Event Bus — is retired. KORA is now a Hermes Agent; no custom
> event bus exists in the active architecture. Historical implementation is
> preserved in Git history (`AI/KORA/Runtime/app/event_bus.py`, pre-retirement).

## Historical (pre-retirement)

General internal messaging boundary for KORA components, co-located in the KORA
process (transport-neutral `EventBus` protocol + `InProcessEventBus`).
