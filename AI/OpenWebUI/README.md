# Open WebUI — KORA UI surface (ADR-0008)

Open WebUI is interaction surface only. Branding and backend routing must present **KORA**.

## Final wiring (Phase 14 closeout)

```text
Open WebUI  --OpenAI API-->  Hermes api_server (hermes:8642/v1, model "KORA")
                                  ↓
                          KORA HEAD AGENT --> Ollama / Honcho / Chroma / Graphify / MCP
```

The standalone KORA Runtime is retired; KORA is a Hermes Agent. Open WebUI also
exposes permitted Ollama models (`qwen3:8b`, `gpt-oss:20b-cloud`) via the
OpenAI-compatible Ollama connection (`http://ollama:11434/v1`).

Compose SoT: `services/open-webui/`

## SoT boundaries (critical)

Open WebUI may store **application runtime data** under `/mnt/monarch/appdata/open-webui`
(chats, UI `vector_db`, uploads, embedding caches). That data is **not** KORA Memory
or Knowledge Source of Truth.

Canonical boundary file: `Config/sot_boundaries.yaml`

Phase 14.2 preflight: `Documentation/Phase14/Phase14.2/`
