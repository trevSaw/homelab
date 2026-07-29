# Ollama

Service documentation placeholder for Ollama.

## Overview
- Purpose: Not documented — requires future operational definition.
- Category: AI
- Current lifecycle state: Not documented — requires future operational definition.
- Importance level: Not documented — requires future operational definition.

## Repository Location
- Service directory: `homelab/Services/ollama.md`
- Compose file: `homelab/Services/ollama/compose.yml`
- Environment template: `homelab/Services/ollama/.env.example` (copy to `.env` on host; never commit `.env`)
- Documentation path: `homelab/Documentation/services/ollama/ollama.md`

## Runtime Information
- Container names: `ollama`, `open-webui`
- Images: `ollama/ollama:latest`, `ghcr.io/open-webui/open-webui:main`
- Ports: none published on host (Traefik for open-webui)
- Networks: `ollama-net`, `proxy`, `ai-assistant`
- Volumes: `/hive/ollama`, `/mnt/monarch/appdata/open-webui`
- Restart policy: `unless-stopped`
- Environment files: `Services/ollama/.env` (`OLLAMA_API_KEY`, `WEBUI_SECRET_KEY`)
- Dependencies: provides `ollama-net` to hermes / honcho / odysseus consumers

## Architecture Relationships
- Upstream dependencies: NVIDIA GPU reservation (optional; `CUDA_VISIBLE_DEVICES=-1` currently disables GPU)
- Downstream consumers: open-webui, hermes, honcho, odysseus (via `ollama-net` / API)
- Network relationships: `ollama-net` (bridge), `ai-assistant` (external), `proxy` (open-webui)
- Reverse proxy relationships: open-webui via Traefik Host `chat.fatherfankscloud.uk`

## Security Review
- Secret handling approach: Compose uses `${OLLAMA_API_KEY}` / `${WEBUI_SECRET_KEY}` via `env_file: .env` (Phase 10). Rotate keys that previously lived in Git history.
- Privileged mode status: false
- Docker socket exposure: none
- External exposure: open-webui via Traefik (`chat.fatherfankscloud.uk`); ollama Traefik disabled
- Known risks: R2 partially mitigated (healthchecks added); R3 memory limit present on ollama (`12g`); image tags still `latest`/`main` (deferred pin)

## Operational Notes
- Backup considerations: Not documented — requires future operational definition.
- Recovery notes: Not documented — requires future operational definition.
- Monitoring requirements: Not documented — requires future operational definition.
- Maintenance considerations: Not documented — requires future operational definition.

## Governance Metadata
- ADR references: []
- Phase 9.1 references: Master_Service_Inventory.md, Runtime_Configuration_Inventory.md
- Migration priority: P2
- Migration wave: Wave 2

### Evidence References

Classification:
- Source: Service_Classification_Matrix.md
- Service: ollama

Runtime:
- None identified.

Dependencies:
- Source: Dependency_Map.md
- Relationship: Provides ollama-net external network used by odysseus

Risks:
- Source: Risk_Register.md
- Risk: R2: Missing healthchecks
- Risk: R3: Absent resource limits
- Risk: R7: Documentation gaps

Migration:
- Source: Migration_Priority_Matrix.md
- Priority: P2

ADRs:
- None identified.

## Known Issues
- Duplicate service name detected during Phase 9.1 inventory. Consolidation deferred to future migration phase.
- Image tags remain floating (`latest` / `main`) — pinning deferred
- Secrets previously committed in Git history should be rotated on mocha
- Documentation gaps remain in Overview / Operational Notes placeholders
