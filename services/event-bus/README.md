---
title: KORA Event Bus Logical Service
document_type: README
service: event-bus
owner: KORA
status: Active
version: 14.2A
last_reviewed: 2026-08-03
related_documents:
  - Architecture/decisions/ADR-14.2A-001-Internal-Event-Bus.md
  - Documentation/Phase14/Phase14.2A/Event_Bus_Architecture.md
  - Validation/Phase14.2A/
---

# Event Bus

General internal messaging boundary for KORA components.

## Phase 14.2A deployment

Event Bus is a logical service co-located in the KORA process. It has no
standalone container, port, persistence, replay worker, or distributed broker.
Runtime code is in `AI/KORA/Runtime/app/event_bus.py`.

## Interface

- `publish(EventEnvelope) -> delivery_count`
- `subscribe(event_type, handler, event_filter=None) -> Subscription`
- `unsubscribe(Subscription) -> bool`

Envelopes are JSON-serializable and carry event type, event ID, source,
timestamp, correlation ID, schema version, metadata, and payload. Callers must
not depend on synchronous delivery or shared object identity.

## Ownership

The Event Bus owns delivery and subscription routing only. KORA owns policy and
orchestration; domain services own their decisions. The bus is not a Source of
Truth.

## Future boundary

A future ADR may replace the in-process adapter with NATS, Redis Streams, gRPC,
or another transport without changing higher-level interfaces. Delivery
guarantees, persistence, replay, and cross-process ordering are intentionally
undefined in Phase 14.2A.
