# Evidence Coverage Report

**Phase:** 9.4  
**Branch:** `phase9.3`  
**Scope:** Per-service evidence coverage across the six evidence categories defined for `service.json` and Governance Metadata.

**Legend:** ✔ = verifiable evidence present · ⚠️ = no verifiable evidence in Phase 9.1 sources (array empty / None identified)

| Service | Classification | Runtime | Dependencies | Risks | Migration | ADRs |
|---------|----------------|---------|--------------|-------|-----------|------|
| authentic | ✔ | ⚠️ | ⚠️ | ✔ | ✔ | ⚠️ |
| beszel | ✔ | ⚠️ | ⚠️ | ✔ | ✔ | ⚠️ |
| beszel_agent | ✔ | ⚠️ | ⚠️ | ✔ | ✔ | ⚠️ |
| calibre-web | ✔ | ⚠️ | ⚠️ | ✔ | ✔ | ⚠️ |
| code-server | ✔ | ⚠️ | ⚠️ | ✔ | ✔ | ⚠️ |
| CosmoOS | ✔ | ⚠️ | ⚠️ | ✔ | ✔ | ⚠️ |
| echoos | ✔ | ✔ | ✔ | ✔ | ✔ | ⚠️ |
| EchoOS | ✔ | ✔ | ✔ | ✔ | ✔ | ⚠️ |
| hermes | ✔ | ⚠️ | ⚠️ | ✔ | ✔ | ⚠️ |
| homepage | ✔ | ⚠️ | ⚠️ | ✔ | ✔ | ⚠️ |
| honcho | ✔ | ⚠️ | ⚠️ | ✔ | ✔ | ⚠️ |
| Hotio | ✔ | ⚠️ | ⚠️ | ✔ | ✔ | ⚠️ |
| jellyfin | ✔ | ⚠️ | ⚠️ | ✔ | ✔ | ⚠️ |
| n8n | ✔ | ⚠️ | ⚠️ | ✔ | ✔ | ⚠️ |
| NZBget | ✔ | ⚠️ | ⚠️ | ✔ | ✔ | ⚠️ |
| odysseus | ✔ | ✔ | ✔ | ✔ | ✔ | ⚠️ |
| ollama | ✔ | ⚠️ | ✔ | ✔ | ✔ | ⚠️ |
| portainer | ✔ | ⚠️ | ⚠️ | ✔ | ✔ | ⚠️ |
| traefik | ✔ | ⚠️ | ✔ | ✔ | ✔ | ⚠️ |

## Category Totals (of 19 services)

| Category | Covered (✔) | Empty (⚠️) | Source File |
|----------|-------------|------------|-------------|
| Classification | 19 | 0 | `Service_Classification_Matrix.md` |
| Runtime | 3 | 16 | `Runtime_Configuration_Inventory.md` (explicit rows only: EchoOS, echoos, odysseus) |
| Dependencies | 5 | 14 | `Dependency_Map.md` (echoos, EchoOS, odysseus, traefik, ollama) |
| Risks | 19 | 0 | `Risk_Register.md` (R2/R3/R7 universal; R1 EchoOS/echoos; R4 odysseus) |
| Migration | 19 | 0 | `Migration_Priority_Matrix.md` |
| ADRs | 0 | 19 | No `ADR-*.md` files in repository |

## Notes

- Empty categories are intentional: Phase 9.4 only links **verifiable** Phase 9.1 entries. Catch-all “All other services / Not Present” rows were **not** treated as positive evidence.
- ADR arrays remain `[]` / “None identified.” because no Architecture Decision Records exist under `Architecture/decisions/`.
