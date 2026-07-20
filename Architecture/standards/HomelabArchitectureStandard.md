# Homelab Architecture Standard v1.0

## Purpose
Define the high‑level architectural constraints and expectations for the homelab environment. This document is the single source of truth for how the homelab is organized, what standards must be met, and which decisions remain open.

## Design Goals
- **Reliability** – Services must be recoverable via documented backup and restore procedures.  
- **Scalability** – The layout should accommodate new domains and services without disruptive re‑architecture.  
- **Security** – Secrets are never stored in version‑controlled files; network isolation is enforced.  
- **Observability** – Monitoring and logging are mandatory for all services.  
- **Maintainability** – Clear directory and naming conventions simplify onboarding and troubleshooting.  
- **Storage Efficiency** – Minimize unnecessary reads and writes against the HDD pool by keeping configuration, metadata, databases, caches, and frequently modified files on SSD while reserving the HDD/ZFS pool for large, relatively static data.

## Guiding Principles
- Configuration data belongs on fast, reliable storage (SSD).  
- Large, static media assets belong on high‑capacity storage (HDD/ZFS).  
- All external traffic passes through a reverse‑proxy with TLS termination.  
- Internal service‑to‑service traffic never traverses the public internet.  
- Secret values are supplied at runtime via environment files, never baked into configuration files.  
- **Separate Application State from Stored Content** – Configuration changes frequently while media changes slowly; the architecture isolates these concerns to ensure recoverable configuration and durable media.

## Domain Layout
| Domain | Responsibility |
|--------|-------------------|
| **Infrastructure** | Core reverse‑proxy, host‑level networking, and base platform services. |
| **AI** | Model serving, inference engines, and related orchestration. |
| **Monitoring** | Metrics collection, dashboards, and alerting. |
| **Storage** | ZFS pools, snapshot policies, and backup orchestration. |
| **Media** | Downloaders, media managers, and streaming services. |
| **Automation** | Home‑assistant, scripting hosts, and orchestration helpers. |
| **Productivity** | Self‑hosted collaboration tools (e.g., Nextcloud, CalDAV). |
| **Development** | Code‑server, build environments, and developer tooling. |

Each domain resides in a top‑level folder under the repository root (`/home/user/homelab/`).

## Directory Standards
- Configuration directories (`*/config`, `*/data`) reside on SSD for fast I/O.  
- Large file repositories (media downloads, backups) reside on HDD/ZFS pools.  
- All service folders contain a `README.md` scaffold describing the service.  
- Global `.gitignore` must exclude any `.env` files containing secrets.

## Networking Standards
- **proxy network** – Public‑facing services expose only HTTP(S) via the reverse‑proxy.  
- **internal network** – Private communication between services (databases, AI models, monitoring agents).  
- **vpn network** (optional) – Media services that require outbound VPN routing attach to this network in addition to `proxy`.  
- **gpu network** (optional) – Services requiring GPU devices attach here.  
- Every container must attach to at least one core network; host ports are never exposed directly.

## Storage Standards
- **SSD policy** – Store configuration, metadata, and frequently accessed data.  
- **HDD/ZFS policy** – Store bulk media, backups, and immutable archives.  
- **Persistent Docker data** – Bind‑mount persistent Docker data under `/monarch` whenever practical; avoid anonymous Docker volumes unless a documented reason exists.  
- **Snapshot cadence** – Daily recursive snapshots of SSD datasets; weekly/monthly retention as defined in the backup policy.  
- **Off‑site storage** – Snapshots are exported, compressed, and stored off‑site (cloud bucket or external drive).

## Secret Management Standards
- Each service provides two files:  
  - `.env.example` – Committed to the repo, lists all required variables with placeholder values.  
  - `.env` – Not committed, contains actual secrets; ignored via global `.gitignore`.  
- Compose files reference variables exclusively via `${VAR}` syntax.  
- Secrets are never hard‑coded in Docker‑Compose or other configuration files.

## Docker Compose Standards
- Use a recent Compose schema version (≥ 3.9).  
- Do **not** include host‑port mappings; expose services through the `proxy` network and reverse‑proxy labels.  
- All services must include `restart: unless-stopped`.  
- External networks (`proxy`, `internal`, `vpn`, `gpu`) are referenced rather than defined inline.  
- Compose files reside inside the service’s domain folder.

## Container Standards
- Define sensible CPU and memory limits for each container.  
- Provide a healthcheck command that returns success on a healthy state.  
- Pin images to exact tags; upgrades are performed by updating the tag and redeploying.  
- Maintain a `Versions.md` per domain listing current image tags for audit purposes.

## Reverse Proxy Standards
- All external HTTP(S) traffic terminates at a centrally managed reverse‑proxy.  
- Services expose no host ports; routing is handled via reverse‑proxy labels.  
- TLS certificates are centrally managed by the reverse‑proxy.  
- Middleware (e.g., authentication, rate‑limiting) is defined in the reverse‑proxy static configuration.

## Backup Standards
### SSD (/monarch)
The SSD is the authoritative source of application state. Daily snapshots capture everything required to rebuild the homelab, including:
- Docker Compose files
- Architecture documentation
- README files
- ADRs
- Configuration
- Databases
- Metadata
- Persistent application data
- Container configuration
- Scripts
- Environment files (`.env`)
- Reverse proxy configuration
- Monitoring configuration

Restoring the SSD snapshot and starting the compose stacks fully restores the homelab configuration.

### HDD (/hive)
The HDD/ZFS pool stores bulk data such as:
- Movies
- TV
- Music
- Downloads
- Photos
- Documents
- Archives
- Game libraries
- Large media collections

This data is intentionally separated from application state; routine architecture snapshots do not include it. The purpose of `/hive` is capacity, not configuration.

### Disaster Recovery Workflow
1. Restore the SSD snapshot.  
2. Mount the HDD/ZFS pool.  
3. Deploy Docker Compose stacks.  
4. Services automatically reconnect to existing media stored on `/hive`.

The architecture intentionally separates "application state" from "stored content."

## Documentation Standards
- Every service folder includes a `README.md` scaffold with: overview, architecture diagram, requirements, installation command, configuration details, backup coverage, update procedure, troubleshooting, and disaster‑recovery steps.  
- A top‑level `backup/README.md` explains snapshot creation, storage location, and restore instructions.

## Naming Standards
- **Folders** – Lower‑case, hyphen‑separated (e.g., `media/qbittorrent`).  
- **Containers** – Match the service name (e.g., `qbittorrent`).  
- **Networks** – `proxy`, `internal`, `vpn`, `gpu`.  
- **Environment variables** – Upper‑case, underscore‑separated, prefixed with the service name where appropriate.

## Security Standards
- No secrets are stored in version‑controlled files.  
- Containers run with the principle of least privilege (drop unnecessary capabilities, read‑only rootfs where possible).  
- SELinux/ZFS labeling (`:z` or `:Z`) is applied to all bind‑mounts.  
- External access is limited to the `proxy` network; internal services are isolated.

## Review Checklist
- [ ] Verify each service folder contains a compliant `README.md`.  
- [ ] Ensure all compose files reference external networks only.  
- [ ] Confirm secret handling follows the `.env.example` / `.env` pattern.  
- [ ] Validate resource limits and healthchecks are defined.  
- [ ] Check backup policy covers all required datasets.  
- [ ] Confirm the reverse‑proxy is the sole public entry point.

## Known Open Decisions
- **GPU network activation** – Whether to enable a dedicated `gpu` network for all GPU‑enabled services.  
- **VPN network scope** – If additional non‑media services should also attach to the VPN network.  
- **Retention policy granularity** – Exact numbers of daily/weekly/monthly snapshots to retain.  
- **Future domain additions** – Criteria for introducing new top‑level domains.

## Final Architecture Review
- **Clarifications**: Backup philosophy now distinguishes SSD (/monarch) and HDD (/hive); disaster‑recovery workflow added; Storage Standards include bind‑mount rule; Guiding Principles include separation principle; Design Goals include Storage Efficiency.
- **Assumptions**: `/monarch` and `/hive` mount points exist and are used consistently.
- **Remaining ambiguities**: None identified; all statements are consistent.
- **Readiness**: Document is now ready to be frozen as Version 1.0.
