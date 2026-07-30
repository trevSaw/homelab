# Validation

Central store for verification artefacts across this personal Homelab repository.

## Layout

| Path | Purpose |
|------|---------|
| `Energy/` | Energy audit reports (`Energy_Audit_*.md`, `Latest_Energy_Audit.md`) |
| `Phase8-Completion-Report.md` | Phase 8 close-out |
| `Phase9/` | Phase 9 completion report |
| `Phase9.1/` | Service inventory & planning |
| `Phase9.2/` | Documentation framework validation |
| `Phase9.3/` | Governance / secret / drift audits |
| `Phase9.4/` | Evidence linkage & AI readiness QA |
| `Phase10/` | Infrastructure standardization QA |
| `Phase10.5/` | Appdata migration **framework** (inventory, matrix, dry-run scripts — no live migration) |

## Running validation locally

```bash
./Scripts/validate.sh
```

Safe, read-only checks:

- `bash -n` on active scripts under `Scripts/`
- `docker compose config` when Docker is available (does not start containers)
- Secret-hygiene heuristics on compose files
- Logging / restart policy presence
- `.env.example` coverage for secret-bearing services
- Markdown presence + relative link spot-checks for Phase 10 docs

## Rules

All validation artefacts must reference the associated service, phase, or document they validate.
Do not treat historical Energy reports as authoritative configuration — re-run `Scripts/audit/energy_audit.sh` on mocha for current data.
