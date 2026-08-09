# Phase 14.4 — Architecture Compliance Audit

**Method:** Code inspection + runtime verification.

## Boundaries

| # | Requirement | Evidence | Result |
| --- | --- | --- | --- |
| 1 | Knowledge ≠ Memory | Graph objects are derived graph representation; never stored as Memory | ✅ |
| 2 | Graphify ≠ Chroma | Graphify handles entities/edges; Chroma handles vectors; no overlap | ✅ |
| 3 | Open WebUI not Knowledge authority | `sot_boundaries.yaml` unchanged; KORA owns retrieval | ✅ |
| 4 | EventBus canonical | `GraphIndexingCoordinator` subscribes via existing `EventBus` | ✅ |
| 5 | Graphify is derived representation | Entities/relationships carry source Knowledge id/version/hash | ✅ |
| 6 | Deterministic entity identity | `entity_id(type, name)` is stable | ✅ |
| 7 | Graph indexing idempotent | Same version+content → no-op | ✅ |
| 8 | Replace-on-success | New representation computed before stale deleted | ✅ |
| 9 | Graph failure safe | Graph backend failure → degraded retrieval; Knowledge unaffected | ✅ |
| 10 | Provenance preserved | Every entity/relationship retains source Knowledge | ✅ |
| 11 | No future-phase functionality | No MCP tools, Council, agents, automation, tool runtime | ✅ |

## Runtime verification

- `pytest`: 138 passed.
- KORA `homelab/kora-runtime:14.4.0` healthy; health graph block: `enabled: true`,
  `provider: graphify`, `graph_healthy: true`.
- Chroma `kora-chromadb` independent project, data volume preserved.
- Graphify `homelab/graphify:14.4.0` healthy; MCP initialize returns 200 + session.
- End-to-end: ingest → semantic index → graph extraction (entities/relationships)
  → graph store → export `graph.json` → Graphify serves (graph_stats: nodes/edges) →
  KORA `get_node` via MCP → combined context with graph evidence.
- Chat path: architecture query → `stores_queried: ['knowledge','graphify']`;
  preference → graphify skipped.
