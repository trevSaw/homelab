# Open WebUI — KORA UI surface (ADR-0008)

Open WebUI is interaction surface only. Branding and backend routing must present **KORA**.

## Stage 1 wiring

```text
Open WebUI  --OpenAI API-->  KORA Runtime  -->  Ollama
```

Direct Open WebUI → Ollama is the legacy path and must not remain the production default after cutover.

Compose SoT: `services/open-webui/`

## SoT boundaries (critical)

Open WebUI may store **application runtime data** under `/mnt/monarch/appdata/open-webui`
(chats, UI `vector_db`, uploads, embedding caches). That data is **not** KORA Memory
or Knowledge Source of Truth.

Canonical boundary file: `Config/sot_boundaries.yaml`

Phase 14.2 preflight: `Documentation/Phase14/Phase14.2/`
