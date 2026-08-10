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

Hermes remains a thin execution layer and is **not** the product identity. Memory, Knowledge, Tools, and MCP are delivered as services orchestrated by the KORA Runtime in later roadmap phases (14.3 Knowledge Platform, 14.4 Knowledge Graph, 14.5 Tool Platform). Council reasoning and agents are planned in Phase 15 (Council & Intelligence) and Phase 16 (Automation & Autonomous Workflows).
