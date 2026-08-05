# Memory Runtime Foundation Architecture

## Component responsibilities

| Component | Owns | Does not own |
| --- | --- | --- |
| KORA | Orchestration, producer policy, user-facing identity | Message transport internals |
| Event Bus | Envelope delivery, subscriptions, routing | Policy, domain decisions, SoT |
| Memory Runtime | Candidate normalization/eligibility, proposal lifecycle coordination | Approval transitions, durable storage |
| Approval Engine | Proposal state transitions | Candidate generation, persistence, UI |
| Honcho | Future durable persistence only | Policy, approval, proposal generation |
| Open WebUI | Interface and request capture | KORA Memory SoT |

## Event-to-proposal flow

```text
Producer
  → KORA policy
  → Event Bus
  → Memory Runtime subscription
  → normalize / enrich / eligibility
  → draft proposal
  → Approval Engine
  → pending_review
```

The bus is general-purpose. Memory Runtime subscribes to relevant namespaces but
does not infer candidates from arbitrary payloads. `memory.candidate` events
carry a candidate directly; other event types must include an explicit
`memory_candidate` object. Low-confidence, disabled-category, disabled-source,
empty, or secret-like candidates are ineligible.

## Proposal model

The ephemeral proposal contains:

- identity/source: `proposal_id`, `source`, `timestamp`, `conversation_id`
- classification: `candidate_type`, `confidence`, `importance`
- intent/content: `proposed_operation`, `proposed_content`
- relationships: `related_entities`, `related_topics`
- lifecycle: `status`, `created_at`, `expires_at`
- governance: `audit_metadata`, source event, correlation ID, schema version

## Lifecycle

```text
draft
  → pending_review
      ├── approved
      ├── rejected
      ├── expired
      └── withdrawn
```

Approval Engine is the only transition owner. Approval changes ephemeral state
only; it does not write to Honcho. Repeated event IDs are idempotent. A
semantically duplicate candidate is recorded as `withdrawn` and references the
existing proposal.

All proposals and audit transitions are lost when the KORA process restarts.
