# beszel_agent

Documentation placeholder for beszel_agent. Detailed documentation will be added during Phase 9.3.
## Overview
- Purpose: Not documented — requires future operational definition.
- Category: Monitoring
- Current lifecycle state: Not documented — requires future operational definition.
- Importance level: Not documented — requires future operational definition.

## Repository Location
- Service directory: `homelab/Services/beszel_agent.md`
- Compose file: `homelab/Services/beszel_agent/compose.yml`
- Environment template: `homelab/Services/beszel_agent/.env.example`
- Documentation path: `homelab/Documentation/services/beszel_agent/beszel_agent.md`

## Runtime Information
- Container names: `beszel-agent`
- Images: `henrygd/beszel-agent`
- Ports: host networking on listen port `45876`
- Networks: `network_mode: host` (required by agent design; exception to core-network preference)
- Volumes: Docker socket (ro), `./beszel_agent_data`
- Restart policy: `unless-stopped`
- Environment files: `Services/beszel_agent/.env` (`KEY`, `TOKEN`, `HUB_URL`)
- Dependencies: Beszel hub on mocha:8090

## Architecture Relationships
- Upstream dependencies: Beszel hub (`HUB_URL`)
- Downstream consumers: none (agent pushes metrics to hub)
- Network relationships: host networking
- Reverse proxy relationships: none

## Security Review
- Secret handling approach: Hub `KEY` / `TOKEN` moved to `.env` (Phase 10). Rotate credentials previously committed in Git history.
- Privileged mode status: false
- Docker socket exposure: read-only (`/var/run/docker.sock:ro`)
- External exposure: host network listener (LAN)
- Known risks: host networking; Docker socket access; healthcheck deferred (host network agent)

## Operational Notes
- Backup considerations: Not documented — requires future operational definition.
- Recovery notes: Not documented — requires future operational definition.
- Monitoring requirements: Not documented — requires future operational definition.
- Maintenance considerations: Not documented — requires future operational definition.

## Governance Metadata
- ADR references: []
- Phase 9.1 references: Master_Service_Inventory.md, Runtime_Configuration_Inventory.md
- Migration priority: P4‑P5
- Migration wave: Wave 6

### Evidence References

Classification:
- Source: Service_Classification_Matrix.md
- Service: beszel_agent

Runtime:
- None identified.

Dependencies:
- None identified.

Risks:
- Source: Risk_Register.md
- Risk: R2: Missing healthchecks
- Risk: R3: Absent resource limits
- Risk: R7: Documentation gaps

Migration:
- Source: Migration_Priority_Matrix.md
- Priority: P4-P5

ADRs:
- None identified.

## Known Issues
- Duplicate service name detected during Phase 9.1 inventory. Consolidation deferred to future migration phase.
- Missing healthchecks
- Missing resource limits
- Documentation gaps
