# KORA Runtime Retirement

**Date:** 2026-08-11
**Branch:** `phase14-hermes-runtime`
**Scope:** Retire the obsolete standalone KORA Runtime; production stack now reflects the final architecture (KORA = Hermes Agent). No architecture redesign, no replacement infrastructure.

---

## Final architecture (active)

```text
Open WebUI
    │
    ▼
Hermes  (api_server :8642, model "KORA")
    │
    ▼
KORA HEAD AGENT  (Hermes plugin: /opt/data/plugins/kora)
    │
    ├── Honcho   (native provider; workspace "kora", peer "user")  → Primary-user memory
    ├── Chroma   (kora-chromadb)  → Knowledge
    ├── Graphify → Relationships
    ├── Ollama   → Inference
    └── MCP      → Tools
```

## 1. Old KORA Runtime components found

| Component | Location | Type |
|---|---|---|
| KORA FastAPI runtime | `AI/KORA/Runtime/` (`app/main.py` + 13 domain modules) | standalone runtime |
| KORA Knowledge platform | `AI/KORA/Knowledge/` (44 modules) | runtime code |
| KORA Tool platform | `AI/KORA/Tools/` (20 modules) | runtime code |
| Runtime tests | `AI/KORA/{Runtime,Knowledge,Tools}/tests/` (37 files) | runtime tests |
| Runtime skeletons/READMEs | `AI/KORA/{Memory,Context,Council}/` | runtime docs |
| Runtime configs | `AI/KORA/Config/{runtime,memory_runtime,knowledge_runtime,tools,council_registration}.yaml` | runtime config |
| Deployment stack | `services/kora/compose.yaml` (image `homelab/kora-runtime:14.5.0`), `.env`, `scripts/start-solo-stack.sh` | active container (removed) |
| Logical services | `services/memory-runtime/`, `services/event-bus/` READMEs | runtime docs |
| Runtime Dockerfile | `AI/KORA/Runtime/Dockerfile` | runtime build |
| Open WebUI → old runtime route | `services/open-webui/` (`OPENAI_API_BASE_URL=http://kora:8080/v1`), `AI/OpenWebUI/Config/stage1.yaml` | active route (cut over) |

## 2. Components retired

- **Container `kora`**: stopped and removed (`docker compose down`). Persistent bind-mount data at `/mnt/monarch/appdata/kora` **preserved** (graphify still serves the last exported `graph.json`; kept for rollback).
- **Open WebUI route**: cut over from `http://kora:8080/v1` → `http://hermes:8642/v1` (API key = Hermes `API_SERVER_KEY`).
- **Runtime code**: removed from the active working tree (see 3).
- **`services/kora/`, `services/memory-runtime/`, `services/event-bus/`**: marked **RETIRED** in place (preserved in git).

## 3. Python files removed

**110 files** removed (all `git rm`'d, recoverable from git history and the production backup):
- `AI/KORA/Runtime/` — 28 (FastAPI runtime + 14 tests + Dockerfile + requirements)
- `AI/KORA/Knowledge/` — 61 (Knowledge platform + 17 tests)
- `AI/KORA/Tools/` — 26 (Tool platform + 6 tests)
- `AI/KORA/Config/*.yaml` runtime configs (5) and `AI/KORA/{Memory,Context,Council}` READMEs (3)

## 4. Python files retained

**4 files** (KORA Hermes Agent + its test — the "very small" retained footprint):

| File | Role |
|---|---|
| `Documentation/Phase14/Phase14-Migration/staging/plugins/kora/__init__.py` | Hermes v0.17.0 KORA agent plugin (hooks + tools); production copy `/opt/data/plugins/kora` |
| `.../plugins/kora/kora_classify.py` | ported classification/strategy (pure functions) |
| `.../plugins/kora/kora_explain.py` | explainability JSON-lines record store |
| `.../staging/tests/test_kora_hermes.py` | integration test (test-only) |

`pytest.ini` no longer sets `pythonpath = AI/KORA/Runtime AI/KORA`.

## 5. Final Docker services

| Container | Status | Role |
|---|---|---|
| `hermes` | healthy | Runtime (api_server :8642, KORA head agent) |
| `open-webui` | healthy | UI (→ hermes:8642, model KORA) |
| `honcho-api` / `honcho-deriver` / `honcho-postgres` / `honcho-redis` | running | Memory |
| `kora-chromadb` | running | Knowledge (Chroma) |
| `graphify` | healthy | Relationships |
| `ollama` | running (untouched) | Inference |
| `traefik` | healthy | Ingress (open-webui `chat.fatherfankscloud.uk`) |

No `kora` runtime container/network/volume. No obsolete exposed ports.

## 6. Final request path

```text
Open WebUI → Hermes api_server (http://hermes:8642/v1, Bearer API_SERVER_KEY) → KORA head agent → Ollama (+ Honcho/Chroma/Graphify/MCP)
```

Verified: `POST /api/chat/completions` (model `KORA`) returns `KORA ... [KORA]{governance metadata}`.

## 7. Open WebUI KORA naming

- `WEBUI_NAME=KORA`, `DEFAULT_MODELS=KORA`; Hermes advertises model id **`KORA`**. The assistant is presented as KORA.

## 8. Honcho integration

- Native Hermes honcho provider (`memory.provider: honcho`), `honcho.json` → `http://honcho-api:8000`, workspace **`kora`**, `peerName: user`, `aiPeer: kora`, `pinUserPeer: true`.
- Verified: api_server chat turns are persisted to Honcho (peer `user` + assistant peer `kora`); conclusions write/read/semantic-query work.

## 9. Single-user configuration

- Hermes api_server carries no per-user runtime id, so all KORA traffic resolves to the single Honcho peer `user` (workspace `kora`). `pinUserPeer: true` makes this explicit and robust.
- Open WebUI signups disabled (`enable_signup: false`); only two accounts exist (Trevor admin, Tracy user).

## 10. Partner isolation

- **Tracy (partner, role `user`)** has **no KORA access** — KORA is an external connection
  model not granted to her and is filtered by Open WebUI's model access control for
  non-admin users. Verified: requesting model `KORA` as Tracy returns `400 Model not found`.
- **Tracy** has access to the permitted Ollama models **`qwen3:8b`** and **`gpt-oss:20b-cloud`**
  via the OpenAI-compatible Ollama connection (`model_ids` filter) + model access grants.
- **Trevor (primary, admin)** sees model KORA and the two permitted Ollama models; he can chat.
- No custom authorization code was added — Open WebUI's native connection + model access
  controls provide this directly. Partner account untouched.

## 11. Tests performed

| # | Test | Result |
|---|---|---|
| 1 | KORA appears in Open WebUI as model "KORA" (Trevor) | ✅ |
| 2 | Open WebUI → Hermes → KORA → Ollama chat | ✅ `OK` + `[KORA]{governance}` |
| 3 | Harmless memory write (tea-over-coffee preference) → peer `user` | ✅ |
| 4 | Memory retrieval (list + semantic query) | ✅ |
| 5 | Restart hermes → KORA works + Honcho memory persists | ✅ |
| 6 | Trevor → qwen3:8b and gpt-oss:20b-cloud respond | ✅ |
| 7 | Tracy → qwen3:8b and gpt-oss:20b-cloud respond | ✅ |
| 8 | Partner isolation: Tracy cannot use KORA (400 "Model not found") | ✅ |
| 9 | Old runtime: container removed, Open WebUI points at hermes:8642 | ✅ |

## 12. Production health

All remaining services healthy (`open-webui`, `hermes`, `graphify`, `ollama`, `traefik`,
honcho suite). Note: Honcho dialectic `.chat()` remains slow because `qwen3:8b` is CPU-bound
in Ollama — a separate model/runtime decision, out of scope here. A honcho-ai SDK `create`
persisted a duplicate test conclusion (honcho-api v3.0.10 create quirk observed; harmless
test data).

## 13. Git commits

- `367c783` — checkpoint pre-retirement (live Hermes compose state).
- `9ee4b59` — KORA Runtime retirement (retirement changes committed).
- `9ca2767` — Honcho connectivity fix (dialectic/dream via Ollama; embedding dim 768).
- Closeout docs (this phase): committed as `docs/...` after this report.

## 14. Rollback procedure

1. Restore retired files from git: `git checkout <pre-retirement-commit> -- AI/KORA services/kora` (or restore from backup `PHASE14-KORA-RUNTIME-FINAL-BACKUP-20260810/tree`).
2. Rebuild/restart old runtime: `cd services/kora && docker compose up -d --build`.
3. Cut Open WebUI back: `services/open-webui/.env` → `OPENAI_API_BASE_URL=http://kora:8080/v1`, `OPENAI_API_KEY=sk-kora-local`, `DEFAULT_MODELS=qwen3:8b`; `docker compose up -d` in `services/open-webui`.
4. Data at `/mnt/monarch/appdata/kora` was never deleted and is still intact.
