# Phase 14.3 — Test Results

**Date:** 2026-08-09

**Command:**

```bash
PYTHONPATH=AI/KORA/Runtime:AI/KORA python3 -m pytest
```

**Result:** `102 passed, 2 warnings in 0.89s`

## Breakdown

| Suite | Count | Status |
| --- | --- | --- |
| Runtime (Phase 14.2 Memory/API/auth) | existing | ✅ |
| Knowledge (Phase 14.2C foundation) | existing | ✅ |
| New Phase 14.3 Knowledge tests | 55 | ✅ |
| New Runtime Knowledge integration tests | 3 | ✅ |
| **Total** | **102** | ✅ |

## New test files

| File | Coverage |
| --- | --- |
| `AI/KORA/Knowledge/tests/test_chunking.py` | Deterministic chunking, overlap, config validation |
| `AI/KORA/Knowledge/tests/test_embedding.py` | Provider abstraction, success, failure, wrong count |
| `AI/KORA/Knowledge/tests/test_vector_store.py` | In-memory store, metadata filtering, idempotency, Chroma adapter (mock transport), unavailable Chroma |
| `AI/KORA/Knowledge/tests/test_index_metadata.py` | In-memory + SQLite round-trip, replace, failed state |
| `AI/KORA/Knowledge/tests/test_indexing.py` | Index pipeline, idempotency, content change + retire, embedding failure, event-driven, index preserved on failure |
| `AI/KORA/Knowledge/tests/test_retrieval.py` | Provenance, top-k, empty, degraded backend, context assembly |
| `AI/KORA/Knowledge/tests/test_service_facade.py` | Version identity, facade compose, ingest→index→retrieve |
| `AI/KORA/Runtime/tests/test_knowledge_runtime_integration.py` | Chat-path retrieval (architecture), skip (preference), graceful failure |

## Notes

- 2 warnings = pre-existing FastAPI `@app.on_event("startup")` deprecation.
- All Chroma/embedding tests use `httpx.MockTransport`; no live service required.
- Full Phase 14.2 behavior preserved; only the Phase 14.2D strategy assertion was
  updated to reflect Phase 14.3's classification-driven Knowledge retrieval.
