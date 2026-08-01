# KORA Runtime — Phase 14.1 Stage 1 (Solo)

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

## Out of scope (later phases)

- Memory Runtime, Knowledge Runtime, Tools/MCP
- Multi-member Council deliberation
- Autonomous agents

Compose SoT: `services/kora/compose.yaml`
