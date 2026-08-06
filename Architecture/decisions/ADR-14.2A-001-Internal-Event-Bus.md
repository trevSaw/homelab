# ADR-14.2A-001 — Introduce Internal Event Bus

**Status:** Approved  
**Date:** 2026-08-03  
**Phase:** 14.2A  
**Decision owner:** KORA architecture

## Context

Phase 13 established KORA as the orchestration and policy authority and assigned
clear ownership to Memory, Knowledge, Tools, Council, and interface layers.
Those responsibilities remain authoritative.

As more internal components are introduced, direct component-to-component
invocation would couple producers to deployment details and make later
separation unnecessarily disruptive. Phase 14.2A needs a transport-neutral way
for KORA components to exchange events while preserving policy and provenance.

## Decision

Adopt an internal Event Bus as KORA's canonical internal communication
mechanism.

The Event Bus is an additive implementation refinement, not a transfer of
authority:

The Event Bus is an internal implementation detail of KORA. External
interfaces continue to interact with KORA rather than communicating directly
with the Event Bus.

- KORA remains the orchestration and policy authority.
- The Event Bus owns internal message delivery and decoupling, not policy.
- Memory Runtime owns proposal generation and proposal lifecycle coordination.
- Approval Engine alone owns proposal state transitions.
- Honcho may provide future durable persistence only; it never decides policy.
- Open WebUI remains an interface and is never a Source of Truth.

Components publish serializable event envelopes and subscribe through a stable
interface. Envelopes include event type, event ID, source, UTC timestamp,
correlation ID, schema version, metadata, and payload. Higher-level components
must not depend on delivery timing, shared object identity, or other in-process
behavior.

Phase 14.2A uses an in-process adapter and co-locates Event Bus, Memory Runtime,
and Approval Engine in the KORA process. These are architectural service
boundaries, not deployment boundaries. A future adapter may use NATS, Redis
Streams, gRPC, or another transport without changing higher-level KORA
interfaces.

The bus is general-purpose. It is not centered on Memory. Memory Runtime
subscribes to relevant events, evaluates explicit candidate data, and decides
whether to create a proposal. No event persistence or replay mechanism is
authorized in this phase, although envelopes are serializable so replay can be
added later.

## Alternatives Considered

### Direct component invocation

Simple for the first implementation, but couples producers to Memory Runtime
and conflicts with the required future separation of logical services.

### Deploy a distributed broker now

Offers cross-process delivery and replay options, but adds operations,
persistence, and failure modes that Phase 14.2A explicitly excludes.

### Make the Event Bus a Memory-specific queue

Smaller initial scope, but creates the wrong ownership boundary and would not
support future Knowledge, Tool, MCP, Graphify, or automation events.

## Consequences

- Producers and consumers depend on stable interfaces and serializable
  envelopes rather than concrete transports.
- KORA policies still govern which events may be produced and consumed.
- Subscriber failure is isolated from other subscribers.
- The in-process adapter is volatile: restart loses events, subscriptions, and
  proposal state.
- Delivery guarantees, persistence, replay, ordering across processes, and
  distributed backpressure remain undefined until a future transport ADR.
- Existing Phase 13 diagrams that show conceptual invocation are refined to
  route internal messages through the Event Bus; ownership does not change.

## Implementation Notes

- Implement `publish`, `subscribe`, and `unsubscribe` behind an `EventBus`
  interface.
- Validate that every accepted envelope can be JSON serialized.
- Use exact and namespace-wildcard topic subscriptions plus metadata/payload
  filters.
- Keep Memory proposal creation event-driven; no Open WebUI or external service
  directly invokes Memory Runtime.
- Do not add Honcho clients, durable writes, event stores, replay workers,
  external producer integrations, or standalone deployments in Phase 14.2A.
