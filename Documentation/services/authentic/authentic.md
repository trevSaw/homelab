# authentic

Documentation placeholder for authentic. Detailed documentation will be added during Phase 9.3.
## Overview
- Purpose: Not documented — requires future operational definition.
- Category: Identity
- Current lifecycle state: Not documented — requires future operational definition.
- Importance level: Not documented — requires future operational definition.

## Repository Location
- Service directory: `homelab/Services/authentic.md`
- Compose file: `homelab/Services/authentic/compose.yaml`
- Environment template: `homelab/Services/.env.example` → `Services/.env`
- Documentation path: `homelab/Documentation/services/authentic/authentic.md`

## Runtime Information
- Container names: `authentik-db`, `authentik-redis`, `authentik-server`, `authentik-worker`
- Images: `postgres:16-alpine`, `redis:alpine`, `ghcr.io/goauthentik/server:2024.12.3`
- Ports: none on host (Traefik 9000)
- Networks: `authentik` (bridge), `proxy`
- Volumes: `${PATH_DATA}/authentik/...`
- Restart policy: `unless-stopped`
- Environment files: `Services/.env` (`PG_*`, `AUTHENTIK_SECRET_KEY`, paths/domain)
- Dependencies: PostgreSQL + Redis (in-stack)

## Architecture Relationships
- Upstream dependencies: PostgreSQL, Redis
- Downstream consumers: SSO clients via Traefik
- Network relationships: authentik + proxy
- Reverse proxy relationships: `sso.${DEFAULT_DOMAIN}`

## Security Review
- Secret handling approach: `AUTHENTIK_SECRET_KEY` and DB password via `Services/.env` (Phase 10 removed plaintext compose key). Rotate secret previously in Git history. Worker mounts Docker socket.
- Privileged mode status: worker runs as `root` (existing)
- Docker socket exposure: worker yes
- External exposure: Traefik HTTPS SSO
- Known risks: Docker socket on worker; rotate leaked `AUTHENTIK_SECRET_KEY`


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
- Service: authentic

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
