# code-server

Documentation placeholder for code-server. Detailed documentation will be added during Phase 9.3.
## Overview
- Purpose: Not documented — requires future operational definition.
- Category: Development
- Current lifecycle state: Not documented — requires future operational definition.
- Importance level: Not documented — requires future operational definition.

## Repository Location
- Service directory: `homelab/Services/code-server.md`
- Compose file: `homelab/Services/code-server/compose.yml`
- Environment template: `homelab/Services/code-server/.env.example`
- Documentation path: `homelab/Documentation/services/code-server/code-server.md`

## Runtime Information
- Container names: `code-server`
- Images: `lscr.io/linuxserver/code-server:latest`
- Ports: none on host (Traefik 8443)
- Networks: `proxy`, `ollama_ollama-net`
- Volumes: `/hive/code-server/config`, read-only hive/monarch workspace mounts
- Restart policy: `unless-stopped`
- Environment files: `Services/code-server/.env` (`PASSWORD`)
- Dependencies: none required at runtime

## Architecture Relationships
- Upstream dependencies: none
- Downstream consumers: operators via Traefik
- Network relationships: proxy + ollama network
- Reverse proxy relationships: `code.fatherfankscloud.uk`

## Security Review
- Secret handling approach: `PASSWORD` via `.env` (Phase 10). Quote values containing `#`. Rotate password previously in Git history.
- Privileged mode status: false
- Docker socket exposure: none
- External exposure: Traefik HTTPS password auth
- Known risks: floating `latest` tag; broad read-only host mounts


## Operational Notes
- Backup considerations: Not documented — requires future operational definition.
- Recovery notes: Not documented — requires future operational definition.
- Monitoring requirements: Not documented — requires future operational definition.
- Maintenance considerations: Not documented — requires future operational definition.

## Governance Metadata
- ADR references: []
- Phase 9.1 references: Master_Service_Inventory.md, Runtime_Configuration_Inventory.md
- Migration priority: P4‑P5
- Migration wave: Wave 5

### Evidence References

Classification:
- Source: Service_Classification_Matrix.md
- Service: code-server

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
