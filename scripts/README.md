# Homelab Scripts

Operational scripts for auditing, maintaining, backing up, migrating, and helping with homelab systems.

```
scripts/
├── audit/          # host, docker, compose, network, AI, energy audits
│   └── archive/    # superseded audit script versions
├── maintenance/    # sync, doublecheck, LLM resource helpers
├── backup/         # backup utilities (placeholder)
├── migration/      # Phase 10.5 appdata migration framework (dry-run default)
└── helpers/        # PDF tooling, risk assessment helpers
```

## Quick examples

```bash
# Energy audit (read-only)
./scripts/audit/energy_audit.sh

# Governance audits
./scripts/audit/host_audit.sh
./scripts/audit/docker_audit.sh
./scripts/audit/compose_audit.sh
```

See `scripts/audit/README.md` for energy-audit details.

## Migration framework (Phase 10.5)

```bash
./scripts/migration/inventory.sh --all
./scripts/migration/compose-path-check.sh
./scripts/migration/run-migration.sh --dry-run code-server
```

Default is `--dry-run`. Do not pass `--execute` or `--apply-compose` until you have reviewed `Validation/Phase10.5/` and are ready on mocha.  
Docs: `Validation/Phase10.5/README.md`.
