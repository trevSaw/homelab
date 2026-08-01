# AI Runtime Tree (Phase 14+)

Production runtime home for the **KORA** platform. Architecture contracts remain under `Architecture/ai/`. ADRs remain under `Architecture/decisions/`.

## Layout

| Path | Role |
| --- | --- |
| `KORA/` | Product conductor runtime, config, prompts, and Stage skeletons |
| `Hermes/` | Thin orchestration substrate registration (ADR-0004) |
| `OpenWebUI/` | UI wiring notes (ADR-0008) |

Compose SoT lives under `services/` (`kora`, `ollama`, `open-webui`, `hermes`) per Docker Compose Standard interim layout.

## Stage 1 path (Phase 14.1)

```text
User → Open WebUI → KORA Runtime → Local Ollama → Response
```

Hermes remains a thin execution layer and is **not** the product identity. Memory, Knowledge, Tools, MCP, Council reasoning, and agents are deferred to later Phase 14 stages.
