# Open WebUI — KORA UI surface (ADR-0008)

Open WebUI is interaction surface only. Branding and backend routing must present **KORA**.

## Stage 1 wiring

```text
Open WebUI  --OpenAI API-->  KORA Runtime  -->  Ollama
```

Direct Open WebUI → Ollama is the legacy path and must not remain the production default after cutover.

Compose SoT: `services/open-webui/`
