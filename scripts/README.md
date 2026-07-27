# Homelab Scripts

Operational scripts for auditing, maintaining, backing up, migrating, and helping with homelab systems.

```
scripts/
├── audit/          # host, docker, compose, network, AI, energy audits
│   └── archive/    # superseded audit script versions
├── maintenance/    # sync, doublecheck, LLM resource helpers
├── backup/         # backup utilities (placeholder)
├── migration/      # migration utilities (placeholder)
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
