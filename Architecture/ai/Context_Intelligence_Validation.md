# KORA Context Intelligence Runtime Validation

**Status:** Validated in isolated non-production spike (Phase 13.13)  
**Lab:** `/mnt/monarch/prototypes/kora-spike/` (outside Git)  
**Inputs:** `Context_Intelligence.md`, `Retrieval_Strategies.md`, `Context_Ranking.md`, `Context_Assembly.md`

## Implemented Runtime Behavior

The disposable KORA façade now enforces:

1. Classification before any retrieval
2. Classification-to-strategy selection
3. Explicit store allow/deny gates
4. Per-store context budgets
5. Ranking before Context Assembly
6. Assembly from ranked, budgeted evidence only
7. Explainability fields for classification, strategy, queried/skipped stores, ranking, pruning, budget, confidence, and provenance

Graphify remains excluded; Memory writes and Knowledge promotion remain disabled.

## Retrieval Gate Enforcement

| Classification | Queried | Skipped |
| --- | --- | --- |
| User Preference | Memory | Knowledge, Tools, Agents, Graphify |
| Knowledge Lookup | Knowledge | Memory, Tools, Agents, Graphify |
| Operational Status | Tools | Memory, Knowledge, Agents, Graphify |
| Memory Query | Memory | Knowledge, Tools, Agents, Graphify |
| Project Continuation | Memory + Knowledge | Tools, Agents, Graphify |
| Unknown / Clarification | None | All stores |

The Phase 13.11 preference over-fetch was eliminated: Knowledge budget is `0`, Knowledge is not queried, and no Knowledge evidence reaches assembly.

## Ranking Behavior

Candidates are scored using:

- relevance
- authority
- freshness
- confidence
- provenance
- relationship weight
- safety

Authority affected ordering for Knowledge; fresh Tool evidence received freshness weight; Phase 13 project artifacts received relationship weight. Material conflict counterparts were retained.

## Budget Enforcement

| Strategy | Memory | Knowledge | Tools |
| --- | ---: | ---: | ---: |
| Preference | 3 | 0 | 0 |
| Architecture | 0 | 4 | 0 |
| Conflict | 0 | 5 | 0 |
| Operational | 0 | 0 | 2 |
| Project continuation | 3 | 5 | 0 |
| Clarification | 0 | 0 | 0 |

Budgets are applied after store gating and before Context Assembly.

## Validation Result

All ten scenarios passed. KORA identity, Council boundaries, provenance, no-write rules, no-execution rules, and runtime isolation were preserved.

## Remaining Limitations

1. Classification is deterministic keyword logic, not a production classifier.
2. Open WebUI, Hermes, and Honcho remain boundary adapters rather than full vendor integrations.
3. Chroma is reachable, while fixture retrieval/ranking remains deterministic for validation.
4. Tool evidence is a read-only fixture and does not connect to Phase 12.
5. Budgets are candidate-count limits, not measured token budgets.
6. Ranking weights are validation constants requiring later calibration.
7. Full Council deliberation remains simulated.

## Conclusion

Phase 13.12 Context Intelligence contracts are implementable without changing KORA architecture. The prototype remains disposable and is not production-ready.
