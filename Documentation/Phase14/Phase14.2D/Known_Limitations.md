# Phase 14.2D — Known Limitations

Non-blocking issues discovered or confirmed during production validation.

## 1. FastAPI lifespan migration pending

`AI/KORA/Runtime/app/main.py` uses the deprecated `@app.on_event("startup")`
decorator. This produces a deprecation warning (2 warnings in the test suite).

- **Impact:** Cosmetic; no functional regression.
- **Classification:** Future Enhancement (maintenance).
- **Deferred to:** Future maintenance sprint. Not a Phase 14.2D deliverable.

## 2. Malformed YAML config fails loudly

`_load_yaml` in `AI/KORA/Runtime/app/main.py` returns `{}` for missing files and
non-dict content, but surfaces `yaml.YAMLError` for malformed YAML.

- **Impact:** A malformed `runtime.yaml` / `memory_runtime.yaml` would prevent
  startup rather than degrade gracefully.
- **Classification:** Documentation Issue (documented; no production change
  introduced in 14.2D). Choosing fail-loud over silent-{}-is a deliberate,
  conservative option; it is recorded here for a future decision.
- **Note:** The test suite asserts the current behavior (`yaml.YAMLError` raised)
  so the contract is pinned.

## 3. Honcho deployment validation deferred

`services/honcho/compose.yml` references a `Dockerfile` that is not present in
the repository (only `compose.yml` and `PHASE14.1.md` exist there).

- **Impact:** Honcho build/up cannot be validated from this repository alone.
- **Classification:** Future Enhancement (deployment assets).
- **Status:** Honcho deployment validation deferred until deployment assets
  exist. The running Honcho backend was verified healthy via KORA's `/health`
  and the adapter is covered by unit tests with a mock transport.

## 4. External networks required for compose up

`services/kora/compose.yaml` depends on external networks `ollama_ollama-net`
and `proxy`. These exist in the environment; a fresh environment must create
them first.

- **Impact:** Operational prerequisite only; documented in the compose file.

## 5. In-memory Knowledge store (no persistence)

The Knowledge store is in-memory only (Phase 14.2C scope). Documents do not
survive restart. Durable Knowledge storage is a Phase 14.3 (Knowledge Platform) concern.

- **Classification:** Future Enhancement (scheduled).
