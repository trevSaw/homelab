# Service README Template
<!--
Purpose: This template provides a standardized README for any service in the homelab.
It aligns with the Docker Compose Standard → Documentation Requirements and the Homelab Architecture Standard → Template Guidelines.
All placeholders use the canonical vocabulary defined in the standards.
-->

## Overview
*Provide a concise, high‑level description of the service, its primary function, and the problem it solves.*

## Purpose
*Explain why this service exists in the homelab and how it contributes to the overall architecture.*

## Architecture
*Reference or embed a diagram that shows the service’s placement within the system, including attached networks, storage, and external dependencies.*
*When linking to the diagram, use a relative path such as `docs/architecture-${SERVICE_NAME}.png`.*

## Dependencies
- List other services, databases, message brokers, or external APIs required.
- Indicate any core networks the service depends on (e.g., `internal`, `proxy`).

## Networks
| Network | Reason |
|---------|--------|
| `${NETWORK_NAME}` | Reason for attaching this network (e.g., service‑to‑service communication) |
| internal | Core internal communication |
| proxy | Public access via reverse‑proxy (if applicable) |
| vpn | Optional VPN routing (if applicable) |
| gpu | Optional GPU access (if applicable) |

## Storage
| Mount | Path inside container | Description |
|------|----------------------|-------------|
| `${VOLUME_NAME}` | `/app/data` | Persistent data storage |
| `${CONFIG_PATH}` | `/app/config` | Configuration files (read‑only where possible) |
| `${MEDIA_PATH}` | `/app/media` | Bulk media (optional, mounted on HDD/ZFS) |
| `${BACKUP_PATH}` | `/app/backup` | Backup location (optional) |

## Environment Variables
| Variable | Required | Description |
|----------|----------|-------------|
| `${SERVICE_NAME}` | Yes | Service identifier (matches folder name) |
| `${IMAGE_NAME}` | Yes | Docker image name |
| `${IMAGE_TAG}` | Yes | Exact image tag |
| `${DOMAIN}` | Yes | Hostname or domain used for reverse‑proxy |
| `${SERVICE_PORT}` | Yes | Port the service listens on |
| `${TZ}` | Yes | Timezone (e.g., `UTC`) |
| `${PUID}` | Yes | User ID for non‑root execution |
| `${PGID}` | Yes | Group ID for non‑root execution |
| `${NETWORK_NAME}` | No | Name of a custom network (if used) |
| `${VOLUME_NAME}` | No | Name of a custom volume (if used) |
| `${CONFIG_PATH}` | No | Path to configuration files |
| `${DATA_PATH}` | No | Path to data directory |
| `${MEDIA_PATH}` | No | Path to media directory |
| `${BACKUP_PATH}` | No | Path to backup directory |
| `${SERVICE_PASSWORD}` | No | Service secret (change before deployment) |
| `${SERVICE_API_KEY}` | No | API key (change before deployment) |

*All variables must be defined in `.env.example`. Secrets must never be stored in the compose file.*

## Deployment
```bash
docker compose -p ${SERVICE_NAME} up -d
```
*Replace `${SERVICE_NAME}` with the actual service name. Ensure `.env` is created from `.env.example` beforehand.*

## Validation
```bash
docker compose config
```
*Run the command to verify that the generated Compose file is syntactically correct and conforms to the Docker Compose Standard → Compose File Organization.*

## Backups
- Describe the backup strategy for each persistent volume (e.g., snapshot of `${VOLUME_NAME}` or `${BACKUP_PATH}`).
- Include any scripts or commands used to create backups.

## Restore
- Outline the steps required to restore data from backups, including volume re‑creation and data import.

## Upgrade Procedure
1. Update the image tag in `compose.yaml` (`${IMAGE_NAME}:${IMAGE_TAG}`).
2. Run `docker compose pull` to fetch the new image.
3. Redeploy with `docker compose up -d`.
4. Verify healthchecks and service functionality.

## Monitoring
- List metrics to monitor (CPU, memory, healthcheck status).
- Reference any monitoring tools or labels required by the Docker Compose Standard → Monitoring Guidelines.

## Troubleshooting
- Common failure modes and their remedies.
- Where to find logs (`docker logs ${SERVICE_NAME}`) and how to adjust log retention.

## Known Exceptions
- Document any deviations from the Docker Compose Standard.
- Provide reason, risk assessment, mitigation, rollback plan, and ARB approval signature.

## Lifecycle Status
- Indicate the current lifecycle stage (Draft, Review, Validated, Production, Deprecated, Archived) as defined in the Homelab Architecture Standard → Service Lifecycle.

## Compliance Score
- Provide a brief compliance rating (e.g., 0‑100) based on the Docker Compose Standard checklist.

## Architecture Review
- Summarize the latest architecture review findings and any required actions.

## Version History
| Date | Version | Change Summary | Author |
|------|---------|----------------|--------|
| YYYY‑MM‑DD | 1.0.0 | Initial template creation | {{YOUR_NAME}} |
| YYYY‑MM‑DD | x.x.x | Description of change | {{YOUR_NAME}} |