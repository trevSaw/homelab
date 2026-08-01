# Phase 14.1 — Assumptions

1. Existing Docker network name `ollama_ollama-net` remains the shared AI backend network.
2. `/hive/ollama` continues as the Ollama model bind mount (not moved to `/mnt/monarch`).
3. Open WebUI chat history remains under `/mnt/monarch/appdata/open-webui`.
4. Stage 1 classifier is heuristic (not ML) and sufficient for foundation refusals.
5. Hermes dashboard remains available but is not required for Solo chat.
6. Honcho may keep running unused by the Solo path until Phase 14.2.
7. Traefik certresolver `le` is the Phase 12 canonical resolver.
8. Pinning Open WebUI to the pre-cutover image digest preserves UI behavior.
9. Floating Hermes `:latest` is an accepted temporary governance exception.
10. Phase 12 non-AI fabric is untouched except shared `proxy` attachment already in use.
