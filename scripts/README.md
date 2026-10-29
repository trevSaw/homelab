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

## VPN watchdog (qbittorrent / nzbget)

`scripts/maintenance/vpn-watchdog.sh` detects a dead Mullvad WireGuard tunnel
(stale handshake / no egress) and self-heals:

1. Auto-refreshes the relay public key in `wg0.conf` if Mullvad rotated it
   (Mullvad renumbers + rekeys relays; hostname only covers IP changes).
2. Restarts `qbittorrent` (re-resolves the hostname endpoint).
3. Restarts `nzbget` (re-attaches to qbittorrent's shared netns).

Runs every 5 minutes via fatherfrank's user crontab. Logs:
`~/.local/log/vpn-watchdog.log`. Manual run:

```bash
./scripts/maintenance/vpn-watchdog.sh
```

### n8n + Discord monitoring

`scripts/maintenance/vpn-watchdog-report.sh` emits actionable watchdog events
(recovery / key-rotation fix / unresolved failure) not yet reported, tracking
progress via `~/.local/log/vpn-watchdog-report.state`.

The n8n workflow **VPN Watchdog Monitor** (active, every 5 min) runs that script
via the existing `SSH Password account` credential, then posts any output to a
Discord webhook. Tested end-to-end (execution history: `n8n/database.sqlite` →
`execution_entity`).

## Migration framework (Phase 10.5)

```bash
./scripts/migration/inventory.sh --all
./scripts/migration/compose-path-check.sh
./scripts/migration/run-migration.sh --dry-run code-server
```

Default is `--dry-run`. Do not pass `--execute` or `--apply-compose` until you have reviewed `Validation/Phase10.5/` and are ready on mocha.  
Docs: `Validation/Phase10.5/README.md`.
