# Phase 14.1 — Migration Notes

## Inventory (pre-cutover)

| Service | Live location | Status | Decision |
| --- | --- | --- | --- |
| Ollama | `/hive/ollama/compose.yml` | Production, actively used | **Migrate SoT** to `services/ollama`; **preserve** `/hive/ollama` models; leave running container unless/until project cutover |
| Open WebUI | Co-located in `/hive/ollama` | Production, actively used | **Migrated** to `services/open-webui`; **preserve** `/mnt/monarch/appdata/open-webui`; backend rewired to KORA |
| Hermes | `/mnt/monarch/appdata/hermes` | Prototype running | **Refactor compose** to `services/hermes` (thin layer); **preserve** data; live container unchanged this phase |
| Honcho | `/mnt/monarch/appdata/honcho` | Prototype running | **Remain unchanged** until Phase 14.2 |
| KORA | N/A | New | **Created** `services/kora` + `AI/KORA` |

## Why not replace Ollama / Open WebUI

Replacement would discard models and chat history. Migration reuses bind mounts and container names where practical.

## Why Hermes was not deleted

ADR-0004 keeps Hermes as orchestration substrate for later stages. Stage 1 Solo chat does not route through Hermes; role is narrowed to thin execution layer via registration + docs + governed compose.

## Why Honcho was not integrated

Memory Runtime is Phase 14.2. Integrating now would risk silent writes and Memory≠Knowledge violations.

## Cutover performed (2026-08-01)

1. Built/started `kora` on `ollama_ollama-net` + `proxy`
2. Stopped/removed legacy `open-webui` container only
3. Started `open-webui` from `services/open-webui` with KORA OpenAI base URL
4. Left `ollama` process owned by legacy `/hive/ollama` project (SoT files ready in git)
5. Left Hermes/Honcho running

## Residual cutover (operator)

- Point Docker Compose management of `ollama` at `services/ollama` without destroying `ollama_ollama-net`
- Align Hermes live project working_dir to `services/hermes` when convenient
- Archive `/hive/ollama/compose.yml` open-webui service block as obsolete
