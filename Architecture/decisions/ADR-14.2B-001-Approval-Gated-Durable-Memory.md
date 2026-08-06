# ADR-14.2B-001 — Approval-Gated Durable Memory

**Status:** Approved

**Date:** 2026-08-03

**Phase:** 14.2B

## Context

ADR-0005 authorized a Honcho spike but did not adopt Honcho as KORA's complete
Memory Runtime. Phase 14.2A then established Event Bus, Memory Runtime, Approval
Engine, and ephemeral proposal contracts.

Phase 14.2B needs approved Memory to survive restart without transferring
policy, proposal lifecycle, or Source-of-Truth ownership to Honcho.

## Decision

Adopt Honcho v3 conclusions as the sole durable store for approved KORA Memory,
behind a provider-neutral `DurableMemoryStore` interface and dedicated Honcho
Adapter.

This is a bounded advancement of ADR-0005. Honcho is not adopted as the complete
Memory Runtime and remains unaware of KORA policy.

The approved flow is:

```text
Event Bus
  → Memory Runtime
  → Approval Engine
  → Commit Coordinator
  → Honcho Adapter
  → Honcho
```

The Commit Coordinator is not a policy authority. It only executes persistence
workflow after Approval Engine has completed the authorization decision.

Approval and persistence are separate state dimensions:

- Proposal state: `draft`, `pending_review`, `approved`, `rejected`, `expired`,
  or `withdrawn`
- Persistence state: `not_requested`, `approved_pending_commit`, `committed`,
  or `commit_failed`

A persistence failure never changes an approved proposal back to pending review.

### Runtime SQLite boundary

KORA owns a SQLite database under its existing `/data` volume for:

- pending proposal state
- lifecycle transitions and audit history
- restart recovery metadata
- external durable identifiers, hashes, and consistency checks

SQLite is runtime infrastructure only. It is not a Memory store. Terminal
proposal content is redacted, approved content is never stored there, and
Honcho conclusions are never duplicated there.

### Authentication boundary

KORA protects Memory read and mutation APIs with provider-agnostic Bearer tokens
supplied through environment secrets. Constant-time comparison is mandatory.
Scopes separate read, user approval, and operator lifecycle actions. External
identity providers may be added later but cannot replace KORA authorization.

## Honcho Mapping

The adapter uses direct v3 conclusion create/list operations only. It does not
send sessions or messages to Honcho's derivation pipeline.

Because conclusions have no metadata field, the adapter serializes a versioned
KORA envelope into conclusion content. The envelope carries the approved text,
proposal ID, category, provenance, and correlation fields. Proposal ID is the
idempotency key. Retrieval is exact list/filter decoding; semantic search is not
enabled in this phase.

## Consequences

- Only an Approval Engine-authorized proposal can reach the adapter.
- Rejected, withdrawn, and expired proposals have no persistence path.
- Ambiguous retries reconcile by proposal ID before creating a conclusion.
- SQLite can restore workflow state without becoming a second Memory database.
- A commit failure remains visible as `approved + commit_failed`.
- After restart, a failed commit without a matching Honcho conclusion may
  require a new proposal because approved content is intentionally absent from
  SQLite.
- Open WebUI remains an interface and never communicates with Honcho directly.

## Alternatives Considered

- Store pending proposals in Honcho: rejected because Honcho is approved Memory
  SoT only.
- Store approved content in SQLite for retry: rejected because it creates a
  secondary Memory database.
- Persist before approval: rejected because it bypasses approval governance.
- Use Honcho sessions/messages: rejected because automatic derivation could
  create ungated durable conclusions.

## Implementation Notes

- Adapter retries are bounded and idempotent.
- Approval intent is audited before commit orchestration.
- Startup restores pending proposals, expires due proposals, validates SQLite,
  reconnects to Honcho, and reconciles in-flight commit references.
- Event Bus remains in-process and non-durable; recovery does not use replay.
