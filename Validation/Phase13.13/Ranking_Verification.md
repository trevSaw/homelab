# Ranking Verification

The runtime ranked candidates before Context Assembly using these recorded axes:

- relevance
- authority
- freshness
- confidence
- provenance
- relationship
- safety

## Observations

| Case | Verification |
| --- | --- |
| Architecture | Relevant networking guidance ranked above unrelated material |
| Conflict | High-authority ADR ranked above informal note; both retained |
| Operational | Read-only Tool evidence received freshness weighting |
| Project continuation | Phase 13 roadmap and Project Memory received relationship weighting |
| Preference | No Knowledge candidates existed to rank because strategy gate prevented the query |
| Clarification | No candidates were retrieved or ranked |

All retained items had provenance labels. No safety-filtered or off-strategy item reached Context Assembly in the final run.

## Limitation

Weights are deterministic validation constants, not calibrated production ranking.
