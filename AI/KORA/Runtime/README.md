# KORA Runtime — Phase 14.2A (Solo)

OpenAI-compatible conductor between Open WebUI and local Ollama.

```text
User → Open WebUI → KORA Runtime → Ollama → Response
```

## In scope

- Classification (heuristic Stage 1)
- Context Intelligence strategy selection with stores skipped
- Context Assembly (conversation provenance only)
- Solo conceptual Council (KORA only)
- Explainability metadata on responses (`kora` object)
- Refuse Execute / Administrative by default
- General internal Event Bus abstraction (in-process adapter)
- Ephemeral Memory proposal lifecycle and Approval Engine contracts
- Read-only proposal status APIs

## Out of scope (later phases)

- Durable Memory/retrieval, Knowledge Runtime, Tools/MCP
- Multi-member Council deliberation
- Autonomous agents

## Memory proposal APIs

- `GET /v1/memory/proposals?status=pending_review`
- `GET /v1/memory/proposals/{proposal_id}`

Creation and approval transitions are internal interfaces. No public mutation
API, Honcho adapter, persistence, or approval UI is enabled.

Compose SoT: `services/kora/compose.yaml`
