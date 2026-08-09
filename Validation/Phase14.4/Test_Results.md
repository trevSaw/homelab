# Phase 14.4 — Test Results

**Date:** 2026-08-09

**Command:**

```bash
pytest -q
```

**Result:** `138 passed, 2 warnings`

## Breakdown

| Suite | Count | Status |
| --- | --- | --- |
| Phase 14.2/14.3 regression | 102 | ✅ |
| New Phase 14.4 graph tests | 36 | ✅ |
| **Total** | **138** | ✅ |

## New test files

| File | Coverage |
| --- | --- |
| `AI/KORA/Knowledge/tests/test_graph_models.py` | Entity/relationship identity, provenance, in-memory + SQLite store CRUD, delete-by-knowledge |
| `AI/KORA/Knowledge/tests/test_graph_extraction.py` | Document/heading extraction, references (inline/wikilink), hierarchy, determinism, external-link exclusion |
| `AI/KORA/Knowledge/tests/test_graph_indexing.py` | Index pipeline, idempotency, update/replace, event-driven, unrelated-event isolation, failure safety |
| `AI/KORA/Knowledge/tests/test_graphify.py` | Graphify MCP HTTP client (health, get_node, query_graph, neighbors, unavailable, auth), graph.json export |
| `AI/KORA/Knowledge/tests/test_graph_retrieval.py` | Entity lookup, neighbors, empty/degraded, combined semantic+graph, graph-disabled, context provenance |
| `AI/KORA/Runtime/tests/test_knowledge_graph_runtime_integration.py` | Chat path: architecture→graph queried, preference→graph skipped, backend failure safe |

## Notes

- 2 warnings = pre-existing FastAPI `@app.on_event` deprecation.
- Graphify client tests use `httpx.MockTransport`; no live Graphify required for unit tests.
- Live deployment validated separately (see runtime verification).
