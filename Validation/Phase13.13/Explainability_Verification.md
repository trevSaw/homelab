# Explainability Verification

Every scenario exposed:

- request classification
- retrieval strategy
- queried stores
- skipped stores
- context budget
- ranking decisions
- context pruning
- confidence
- labeled evidence provenance
- Council contributors

Every result also recorded `raw_cot_exposed=false`.

| Requirement | Result |
| --- | --- |
| Classification visible | Pass |
| Strategy visible | Pass |
| Queried/skipped stores visible | Pass |
| Ranking/pruning visible | Pass |
| Confidence visible | Pass |
| Provenance visible | Pass |
| Raw chain-of-thought absent | Pass |
| KORA identity retained | Pass |

The explanation describes accountable process metadata, not hidden deliberation transcripts.
