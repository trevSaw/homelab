# Future Improvements Register

**Phase recorded:** 9.4.1  
**Nature:** Recommendations only — **none of these items were implemented** in Phase 9.4 or 9.4.1.

## Phase 10

| ID | Recommendation | Rationale |
|----|----------------|-----------|
| F10-1 | Normalize duplicated Governance Metadata sections | Three service docs (`beszel`, `jellyfin`, `traefik`) contain duplicate `## Governance Metadata` blocks. See `Duplicate_Governance_Metadata_Report.md`. |
| F10-2 | Expand Runtime Configuration Inventory coverage to all services | Phase 9.1 only has explicit runtime rows for EchoOS, echoos, and odysseus; 16 services correctly have empty `runtime` evidence arrays. |
| F10-3 | Expand Dependency Map coverage where appropriate | Only five services currently have verifiable dependency/network relationships in Phase 9.1. |
| F10-4 | Introduce ADR references once ADR documents exist | `adrs` arrays are empty because no `ADR-*.md` files exist under `Architecture/decisions/`. |
| F10-5 | Consider enriching the evidence schema with additional metadata such as `section`, `value`, and `confidence` | Would improve AI consumability; deferred to avoid schema redesign during Phase 9.4. |
| F10-6 | Consider separating `identified_risks` and `risk_evidence` | Avoids semantic ambiguity between “risks that apply to the service” and “citations proving those risks.” Recommendation only; schema unchanged in 9.4/9.4.1. |

## Explicit Non-Actions (this phase)

- Do not implement F10-1 through F10-6 here.
- Do not invent runtime, dependency, or ADR evidence to fill empty arrays.
- Do not redesign the six-array `evidence` schema during Phase 9.4.1.
