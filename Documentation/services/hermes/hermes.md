# hermes

Documentation placeholder for hermes. Detailed documentation will be added during Phase 9.3.
## Overview
- Purpose: Not documented — requires future operational definition.
- Category: Messaging / Communication
- Current lifecycle state: Not documented — requires future operational definition.
- Importance level: Not documented — requires future operational definition.

## Repository Location
- Service directory: `homelab/Services/hermes.md`
- Compose file: `homelab/Services/hermes/compose.yml`
- Environment template: `homelab/Services/hermes/.env.example`
- Documentation path: `homelab/Documentation/services/hermes/hermes.md`

## Runtime Information
- Container names: `hermes`
- Images: `nousresearch/hermes-agent:latest`
- Ports: none on host (Traefik port 9119)
- Networks: `proxy`, `ollama_ollama-net`
- Volumes: `/mnt/monarch/appdata/hermes`
- Restart policy: `unless-stopped`
- Environment files: `Services/hermes/.env` (dashboard basic auth)
- Dependencies: Ollama at `http://ollama:11434`

## Architecture Relationships
- Upstream dependencies: Ollama
- Downstream consumers: operators via Traefik dashboard
- Network relationships: proxy + ollama-net
- Reverse proxy relationships: `hermes.fatherfankscloud.uk`

## Security Review
- Secret handling approach: `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD` via `.env` (Phase 10). Rotate password previously in Git history.
- Privileged mode status: false
- Docker socket exposure: none
- External exposure: Traefik HTTPS + basic auth
- Known risks: floating `latest` tag; rotate leaked dashboard password


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
- Service: hermes

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
