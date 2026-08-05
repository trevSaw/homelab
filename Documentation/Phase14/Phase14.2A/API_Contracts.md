# Phase 14.2A API Contracts

## Internal Event Bus

```text
publish(EventEnvelope) -> delivery_count
subscribe(event_type, handler, event_filter=None) -> Subscription
unsubscribe(Subscription) -> bool
```

The interface does not promise in-process or synchronous behavior.

## Internal Memory Runtime

```text
create_proposal(EventEnvelope) -> MemoryProposal
list_pending() -> list[MemoryProposal]
get_proposal(proposal_id) -> MemoryProposal
```

Production components create proposals by publishing events. Direct invocation
exists as the logical service contract and for adapter tests; producers must
use the Event Bus.

## Internal Approval Engine

```text
approve(proposal_id, actor="user") -> MemoryProposal
reject(proposal_id, actor="user", reason=None) -> MemoryProposal
expire(proposal_id, now=None) -> MemoryProposal
withdraw(proposal_id, actor="kora", reason=None) -> MemoryProposal
```

`submit` is the internal handoff from draft to pending review. Invalid
transitions fail closed; repeated approval is idempotent. None of these methods
invokes persistence.

## Read-only HTTP API

| Method | Path | Semantics |
| --- | --- | --- |
| `GET` | `/v1/memory/proposals?status=pending_review` | List ephemeral proposals in one state |
| `GET` | `/v1/memory/proposals/{proposal_id}` | Fetch one ephemeral proposal |

Invalid status values return HTTP 422 and missing IDs return HTTP 404.

No create, approve, reject, expire, withdraw, delete, or durable Memory HTTP
endpoint is exposed in Phase 14.2A.
