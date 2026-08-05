# Event Bus Architecture

## Purpose

The Event Bus is KORA's general internal messaging boundary. It decouples
producers and consumers without taking orchestration, policy, or domain
ownership from KORA and its logical services.

```text
KORA policies
     │
     ▼
Event Bus interface
     │
     ├── Memory Runtime
     ├── future Knowledge / Graphify consumers
     ├── future Tool / MCP consumers
     └── future automation consumers
```

## Envelope

Every event has:

- `event_id`, `event_type`, `source`
- UTC `timestamp`
- `correlation_id`
- `schema_version`
- JSON-compatible `metadata` and `payload`

Envelopes support dictionary round trips and are validated as JSON-serializable
when published. Serialization enables a future transport or replay design; this
phase implements neither persistence nor replay.

## Interface and routing

`publish`, `subscribe`, and `unsubscribe` are defined by a transport-neutral
interface. The initial adapter supports exact topics, namespace wildcards such
as `git.*`, and caller-supplied filters. One failed subscriber does not prevent
delivery to others.

Components must not rely on synchronous delivery, shared object identity,
in-process ordering, or volatile subscription internals. Those properties are
adapter details and are not part of the contract.

## Phase 14.2A boundary

The adapter is in-process and volatile. There is no broker, event store,
delivery retry, dead-letter queue, persistence, replay, or cross-process
transport. A future ADR may introduce NATS, Redis Streams, gRPC, or another
adapter behind the same interface.
