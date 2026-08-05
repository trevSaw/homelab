# Phase 14.2 Preflight Assessment

**Date:** 2026-08-01  
**Scope:** Residual ownership migration + SoT boundary confirmation + Memory approval UX design  
**Non-goals:** Honcho durable writes, Knowledge Runtime, Tools/MCP, Council deliberation

---

## Assumptions confirmed

1. Phase 13 docs (`Memory.md`, `Memory_Runtime.md`, ADR-0005/0008/0004) remain authoritative.
2. Docker Compose SoT lives under `services/<name>/` with data on `/mnt/monarch/appdata` or established binds.
3. `ollama_ollama-net` is a shared production network and must not be deleted.
4. `/hive/ollama` is the Ollama **model/runtime data** directory, not the long-term compose project home.
5. Open WebUI data under `/mnt/monarch/appdata/open-webui` is application runtime data, not KORA Memory/Knowledge SoT.

---

## Current state (pre-preflight)

| Concern | Finding |
| --- | --- |
| Ollama compose ownership | Still `/hive/ollama/compose.yml` while git SoT existed at `services/ollama` |
| Ollama data | `/hive/ollama` (models/cache) — production |
| Open WebUI | Already on `services/open-webui`; data at `/mnt/monarch/appdata/open-webui` |
| Hermes compose ownership | `/mnt/monarch/appdata/hermes/compose.yml` |
| Hermes data | `/mnt/monarch/appdata/hermes` — production |
| KORA | `services/kora` live |
| Network | `ollama_ollama-net` shared by ollama, kora, open-webui, hermes, honcho, code-server, odysseus |
| Honcho | Running; not on Solo chat path (correct for pre-14.2) |

### What remained under `/hive/ollama`

| Artifact | Role after preflight |
| --- | --- |
| `models/`, `cache/`, Ollama state | **Retained** as production bind for `/root/.ollama` |
| `compose.yml` | Archived/disabled — ownership moved |
| `.env` | Legacy local secrets file (not git); superseded by `services/ollama/.env` |
| `id_ed25519*` / `history` | Untouched host artifacts; not compose ownership |

---

## Target state

| Concern | Target |
| --- | --- |
| Ollama compose | `services/ollama/compose.yaml` with **external** `ollama_ollama-net` |
| Hermes compose | `services/hermes/compose.yaml` |
| Data binds | Unchanged paths |
| Open WebUI | No mounts into KORA Memory/Knowledge; documented boundaries |
| Memory writes | Design-only approval UX; no Honcho durable write implementation |

---

## Risks

| Risk | Mitigation |
| --- | --- |
| `compose down` deletes `ollama_ollama-net` | Network marked **external** in `services/ollama`; never down legacy hive project |
| Accidental restart from legacy paths | Legacy compose renamed `*.DISABLED-*`; ownership README left in place |
| Secret leakage into git | Secrets only in gitignored `.env` |
| Open WebUI RAG confused with KORA Knowledge | Explicit SoT boundary file + compose comments |
| Premature Honcho writes | Approval UX designed; writes not implemented |

---

## Rollback considerations

See `Migration_Plan.md` rollback sections and Phase 14.1 rollback for UI path.

---

## Acceptance criteria

- [x] Ollama managed from `services/ollama`
- [x] Hermes managed from `services/hermes`
- [x] `ollama_ollama-net` intact with dependents
- [x] Model count unchanged; Hermes data mount unchanged
- [x] Open WebUI has no KORA SoT mounts
- [x] Memory approval UX design published (no writes)
- [x] Validation checklist completed
