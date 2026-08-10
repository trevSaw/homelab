# Phase 14.2D — Validation Checklist

## Automated Tests

| Area | Result |
| --- | --- |
| EventBus lifecycle | ✅ Pass (existing `test_event_bus.py`) |
| Memory proposal lifecycle | ✅ Pass (existing `test_memory_runtime.py`) |
| Approval workflow + API scopes | ✅ Pass (existing `test_memory_api.py`, `test_auth.py`) |
| Durable persistence + restart recovery + idempotency + expiry | ✅ Pass (existing `test_durable_memory.py`) |
| Honcho adapter retry/idempotency | ✅ Pass (existing `test_honcho_adapter.py`) |
| Knowledge document/processor/store/service | ✅ Pass (existing Knowledge tests) |
| Config loading (missing/valid/non-dict YAML) | ✅ Pass (`test_config_loading.py`) |
| Health endpoint shape + Ollama-degraded | ✅ Pass (`test_health_endpoint.py`) |
| Graceful degradation (502, model fallback) | ✅ Pass (`test_graceful_degradation.py`) |
| Chat-path store isolation (no memory/knowledge/tools) | ✅ Pass (`test_graceful_degradation.py`) |
| Knowledge↔Memory isolation | ✅ Pass (`test_isolation.py`) |

**Command:** `PYTHONPATH=AI/KORA/Runtime:AI/KORA python3 -m pytest`

**Result:** 55 passed, 2 warnings (2 warnings = FastAPI `@app.on_event` deprecation, non-blocking)

## Docker Validation

| Check | Result |
| --- | --- |
| `docker compose -f services/kora/compose.yaml build` | ✅ Pass (image built) |
| `docker compose config --quiet` | ✅ Pass |
| Compose up (already running) | ✅ Pass (`kora` running healthy) |
| `/health` endpoint | ✅ Pass (status ok, ollama true) |
| Ollama connectivity | ✅ Pass |
| Chat completion end-to-end | ✅ Pass (200, model response) |
| Restart behavior | ✅ Pass (restart → running healthy) |
| Environment variables | ✅ Pass (config dir, prompts dir, db path, model, tz) |
| Volume mappings | ✅ Pass (config/prompts ro, data rw) |
| SQLite repository integrity | ✅ Pass (integrity ok, 0 terminal-content rows) |

## Operational Validation

| Check | Result |
| --- | --- |
| Config defaults (env overrides) | ✅ Pass |
| Missing config file → empty dict | ✅ Pass |
| Malformed YAML | ✅ Documented limitation (fail-loud) |
| Ollama down → health degraded, chat 502, models fallback | ✅ Pass |
| Startup recovery | ✅ Pass (recovery status ok) |
| Logging | ✅ Present (`KORA_LOG_LEVEL`, basicConfig) |
