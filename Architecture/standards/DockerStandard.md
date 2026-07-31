# Docker Compose Standard v1.0

*Version 1.0 – Authoritative reference for every Docker‑Compose stack within the homelab.*  
*Implementation‑agnostic wherever practical and an extension of the **Homelab Architecture Standard v1.0**.*

---

## 1. Purpose
The purpose of this standard is to guarantee **predictable, secure, and maintainable** Docker‑Compose deployments across the homelab. By enforcing a common structure, naming, and operational expectations, every stack should feel familiar to any engineer, regardless of who authored it. Consistency reduces onboarding time, prevents configuration drift, and enables automated validation.

---

## 2. Scope
**In scope**  
- `compose.yaml` (primary compose file)  
- `compose.override.yaml` (optional local overrides)  
- `.env.example` (committed template for required variables)  
- `README.md` (service‑level documentation)  
- `Versions.md` (image‑tag inventory)

**Out of scope**  
- Application‑specific Dockerfiles (handled by a separate Dockerfile Standard, if present)  
- Runtime scripts that are not part of the compose definition (e.g., backup scripts)  
- Non‑Docker orchestration tools (Kubernetes, Nomad, etc.)

---

## 3. Document Hierarchy

This standard is subordinate to the Homelab Architecture Standard.

If this document conflicts with the Homelab Architecture Standard, the Architecture Standard always takes precedence.

Templates, audits, implementation guides, and automation are subordinate to this standard.

Hierarchy:

Homelab Architecture Standard  
↓  
Docker Compose Standard  
↓  
Templates  
↓  
Audits  
↓  
Docker Compose Stacks

---

## 3. Directory Layout Standard
Compose projects live under `homelab/compose/<domain>/<project>/`, where `<domain>` is one of `ai`, `automation`, `development`, `media`, `monitoring`, `networking`, `productivity`, `security`, or `storage`. The required layout is:

```
homelab/compose/<domain>/<project>/
│   compose.yaml                # Primary compose definition
│   compose.override.yaml      # Optional local overrides (git‑ignored)
│   .env.example                # Template of required environment variables
│   README.md                   # Service documentation (see §14)
│   Versions.md                 # Pinned image versions for audit
│
├── config/                     # Configuration files – stored on SSD (/monarch)
│   └── *.conf
│
├── data/                       # Persistent application data – stored on SSD
│   └── *
│
├── media/                      # Bulk media – bind‑mount to HDD/ZFS (/hive) when needed
│   └── *
│
└── scripts/                    # Helper scripts, idempotent, git‑tracked
    └── *.sh
```

**Production interim (Phase 12.1 pilot, 2026-07-31):** live stacks are standardized under `services/<service>/` with persistent data bind-mounted to `/mnt/monarch/appdata/<service>`. That layout is the **canonical production SoT until** a dedicated directory-layout migration to `compose/<domain>/` is executed. New pilot-compliant stacks MUST include at minimum: `compose.y*ml`, `.env.example`, `README.md`, `Versions.md`, pinned images, restart policy, resource limits, and documented exceptions.

**Rationale:**  
- Mirrors the **Directory Standards** of the Architecture Standard (SSD vs. HDD).  
- Uniform scaffolding (`README.md`, `Versions.md`) guarantees discoverability and auditability.
- Keeps compose projects grouped by functional purpose rather than alphabetically or by deployment date.
- Phase 12.1 proved `services/` + `/mnt/monarch/appdata` as the operational pattern without blocking on a full tree reorg.

---

## 4. Compose File Organization
All `compose.yaml` files must follow the exact ordering of top‑level keys below. Each key appears **once** and **in the listed sequence** (optional sections may be omitted).

1. Compose files shall target the current supported Docker Compose Specification.  
2. `services`  
   - `image`  
   - `container_name`  
   - `hostname`  
   - `restart` (default `unless-stopped`; exceptions must be documented)  
   - `user` (non‑root whenever possible)  
   - `depends_on`  
   - `env_file` (reference `.env.example` or `.env`)  
   - `environment` (additional inline vars)  
   - `volumes` (bind mounts only; named volumes must be declared external)  
   - `devices` (GPU or other host devices)  
   - `networks` (reference external networks only)  
   - `labels` (including reverse‑proxy labels)  
   - `healthcheck`  
   - `logging` (optional – see §12)  
   - `deploy.resources` (CPU/Memory limits)  
3. `networks` (declare as **external**, never defined inline)  
4. `volumes` (declare as **external** when used across services)

*Why strict ordering?* Consistent ordering simplifies diff‑based reviews, automated linting, and visual scanning.

---

## 5. Naming Standards
| Artifact               | Convention                                        | Example                              |
|------------------------|---------------------------------------------------|--------------------------------------|
| **Service name**       | lower‑case, hyphen‑separated, matches folder name| `media-qbittorrent`                  |
| **Container name**     | identical to service name                         | `media-qbittorrent`                |
| **Hostname**           | same as container name                            | `media-qbittorrent`                |
| **Compose project**    | folder name (Docker `-p` flag)                    | `media-qbittorrent`                |
| **Network name**       | one of `proxy`, `internal`, `hotio`, `vpn`, `gpu` (lower‑case) | `internal`                 |
| **Volume name**        | `<service>_<purpose>` (snake_case)                | `media_qbittorrent_data`           |
| **Environment var**    | UPPERCASE, underscore, optionally prefixed with service | `QBITTORRENT_PORT`            |
| **Label key**          | `com.<org>.<service>.<key>`                        | `com.homelab.media.qbittorrent.role` |
| **Directory name**     | lower‑case, hyphen‑separated (see §3)              | `media/qbittorrent`                |

All names must be **predictable**, **unique within the project**, and **consistent with the Architecture Standard naming guidance** (§127‑§131).

---

## 6. Networking Standard
Reference **Architecture Standard – Networking Standards**.

**Core networks** (pre‑created on the host):  

- `proxy` – public‑facing traffic via the reverse‑proxy.  
- `internal` – private service‑to‑service communication.  
- `hotio` – media automation fabric (live Docker network name: `hotio_default`; see Media Stack Networking).  
- `vpn` – optional, for services that need outbound VPN routing.  
- `gpu` – optional, for GPU‑enabled workloads.

**Media domain:** *arr dual-homing, downloader DNS, and Traefik ingress rules are defined in `Architecture/media-stack-networking.md` and override generic examples for media services.

**Rules**  

- Every container must attach to **at least one core network**.  
- **Do not expose host ports directly**; use reverse‑proxy labels for external exposure.  
- **No new networks** may be introduced without explicit Architecture Standard amendment.  
- **Exceptions** (e.g., a dedicated monitoring network) must be documented in the service `README.md` and approved by the Architecture Review Board.

---

## 7. Storage Standard
Reference **Storage Standards** and the SSD/HDD policy.

| Storage class        | SSD (`/monarch`) – bind‑mount path | HDD/ZFS (`/hive`) – bind‑mount path | Recommended mount options |
|----------------------|------------------------------------|------------------------------------|----------------------------|
| **Configuration**   | `config/`                          | –                                  | `:z` (SELinux/ZFS labeling) |
| **Application State**| `data/`                            | –                                  | `:z` |
| **Bulk Media**       | –                                  | `media/` (or service‑specific sub‑folder) | `:z` |
| **Backups**          | `backup/` (SSD)                    | `backup/` (HDD) if large          | `:z` |
| **Caches**           | `cache/` (SSD)                     | –                                  | `:z` |
| **Temporary**        | `tmp/` (SSD)                       | –                                  | `:z` |

**Prohibited:** Anonymous Docker volumes (`volumes:` without `external` or explicit bind‑mount). All persistent data must be a bind‑mount into an approved location.

---

## 8. Environment Variable Standard
- **`.env.example`** – committed, contains **all** required variables with placeholder values (e.g., `MYSQL_ROOT_PASSWORD=change_me`).  
- **`.env`** – **never** committed; listed in global `.gitignore`.  
- **Naming** – UPPERCASE, underscores, optionally prefixed (`SERVICE_`).  
- **Formatting** – `KEY=value` per line; comments begin with `#`.  
- **Defaults** – Provide sensible defaults where a variable can be optional; document in `README.md`.  
- **Secret handling** – Secrets must **never** appear in `compose.yaml` or any version‑controlled file. Use `${VAR}` syntax exclusively.

---

## 9. Security Standard
- **Run as non‑root** (`user:`) whenever the image permits.  
- **Least‑privilege** – drop all unnecessary Linux capabilities (`cap_drop:`) and enable `read_only: true` for rootfs when feasible.  
- **Mounts** – declare `read_only:` on configuration mounts that do not require writes.  
- **Capabilities** – only add `cap_add:` when absolutely required and document justification.  
- **Network isolation** – avoid `network_mode: host`; use only the declared core networks.  
- **PID/IPC isolation** – do not set `pid: host` or `ipc: host` unless formally approved.  
- **Secrets** – always sourced from `.env` or Docker Secrets (Swarm mode is out of scope for this standard).  

*Approved exceptions* (e.g., privileged mode for hardware passthrough) must be recorded in the service `README.md` and receive Architecture Review Board sign‑off.

---

## 10. Resource Management
- **CPU limits** – `deploy.resources.limits.cpus` shall be defined proportionally to the workload; exact values are implementation‑specific and documented per service.  
- **Memory limits** – `deploy.resources.limits.memory` defined in MiB (e.g., `256M`, `1G`).  
- **GPU reservations** – when `devices:` includes a GPU device, the service must attach to the `gpu` network and document the GPU usage requirements.  
- **Restart policy** – default `restart: unless-stopped`. Exceptions require explicit documentation.  
- **OOM behavior** – rely on Docker’s default OOM‑killer; optionally set `oom_score_adj` for critical services.  
- **Requests vs. limits** – When using Swarm mode (future‑proof), define both `reservations` and `limits`.  

*Exceptions* require justification in `README.md`.

---

## 11. Healthchecks
- **Mandatory** for any service exposing a network endpoint or performing background work.  
- **Definition** – `healthcheck:` must include at least `test`, `interval`, `timeout`, `retries`, and `start_period`.  
- **Defaults** – `interval: 30s`, `timeout: 5s`, `retries: 3`, `start_period: 10s`.  
- **Implementation** – prefer lightweight HTTP `curl` checks or native CLI status commands; avoid heavyweight scripts.  

Healthchecks enable the reverse‑proxy to route only healthy instances and assist automated recovery.

---

## 12. Logging Standard
- **Driver** – The default logging driver shall be defined by the host environment; `json-file` is recommended for local development. Alternative drivers (e.g., `syslog`, `fluentd`) may be used when a centralized logging solution is configured (outside the scope of this document).  
- **Rotation** – `max-size: 10m`, `max-file: 5` (implementation‑specific values may be adjusted in the **Implementation Notes** section).  
- **Retention** – logs older than 7 days are rotated out; archival is handled by the central logging system.  
- **Formatting** – JSON‑structured logs are preferred for downstream parsers.  
- **Centralized logging** – required for services handling sensitive data; indicated via a label (`com.homelab.logging=central`).  

---

## 13. Reverse Proxy Integration
Reference **Architecture Standard – Reverse Proxy Standards**.

- `<proxy>.enable=true`  
- `<proxy>.http.routers.<service>.rule=Host(\`example.domain\`)`  
- `<proxy>.http.routers.<service>.entrypoints=websecure`  
- `<proxy>.http.routers.<service>.tls=true`  

*(All concrete “traefik” references have been replaced by the generic `<proxy>` placeholder. The specific reverse‑proxy implementation (e.g., Traefik v3) is defined in the Architecture Standard.)*  

- **Router naming** – `router_<service>`; **middleware** – `middleware_<service>_<function>` (e.g., `middleware_media_auth`).  
- **TLS** – termination always at the reverse‑proxy; services never expose TLS themselves.  
- **Port exposure** – omit `ports:` entirely unless a temporary debugging need is explicitly documented.  

---

## 14. Documentation Requirements
Every service folder must contain **exactly** the following files:

1. `README.md` – includes:  
   - Overview & purpose  
   - Architecture diagram (optional)  
   - Required external resources (networks, volumes, devices)  
   - Installation / deployment command (`docker compose up -d`)  
   - Configuration guide (environment variables, bind‑mount paths)  
   - Backup & restore notes  
   - Upgrade procedure (image tag bump)  
   - Known limitations & troubleshooting steps  
2. `.env.example` – template for required environment variables (see §8).  
3. `Versions.md` – list of pinned image tags with dates and change notes.  

Documentation must be **complete** before a stack can be promoted to production.

---

## 15. Validation Requirements
Prior to any deployment, the following automated checks must pass (can be scripted with `docker compose config` and lint tools):

- `docker compose config` succeeds (valid YAML, schema ≥ 3.9).  
- All required files exist (`compose.yaml`, `.env.example`, `README.md`, `Versions.md`).  
- All referenced **external networks** (`proxy`, `internal`, `hotio`→`hotio_default`, optional `vpn`/`gpu`) exist on the host.  
- All referenced **external volumes** exist (or are declared with `external: true`).  
- No plaintext secrets in any version‑controlled file.  
- Each service defines a **healthcheck** (unless explicitly exempted).  
- `restart: unless-stopped` is present for every service (or documented exception).  
- Images are **pinned** to exact tags (no `latest`).  
- Logging configuration complies with §12.  
- Reverse‑proxy labels are present for every publicly exposed service.  
- Documentation checklist (README, env template, versions) is satisfied.  
- The stack complies with the **Architecture Standard** (network, storage, security).  

Automation can enforce these via a CI pipeline or pre‑commit hook.

---

## 16. Definition of Done
The following checklist determines compliance for a completed compose stack:

- [ ] Directory layout matches §3.  
- [ ] `compose.yaml` follows ordering in §4.  
- [ ] All naming conventions respected (§5).  
- [ ] Only approved core networks are used (§6).  
- [ ] Storage bind‑mounts obey SSD/HDD policy (§7).  
- [ ] `.env.example` present; `.env` ignored (§8).  
- [ ] Security hardening applied per §9.  
- [ ] Resource limits defined as per §10.  
- [ ] Healthcheck defined (or documented exemption) (§11).  
- [ ] Logging driver & rotation set (§12).  
- [ ] `<proxy>` labels correct and no host ports exposed (§13).  
- [ ] Documentation files complete (§14).  
- [ ] All validation checks pass (§15).  
- [ ] Architecture Standard review signed off (link to ADR).  

Only when **all items are checked** may the stack be merged to `main` and deployed.

---

## 17. AI Implementation Rules
AI agents (e.g., automated auditors, formatters) may:

- Reorder sections to match the prescribed order.  
- Format YAML (indentation, quoting) uniformly.  
- Externalize secrets into `.env.example` / `.env`.  
- Insert missing documentation scaffolds (`README.md`, `Versions.md`).  
- Add missing healthchecks or logging defaults where safe.  

AI agents **must NOT**:

- Rename services, containers, or directories.  
- Move data between SSD and HDD locations.  
- Introduce new networks or change existing ones.  
- Upgrade major image versions without explicit human approval.  
- Alter architectural decisions (e.g., disable reverse‑proxy).  

Any prohibited action must be flagged for human review.

---

## 18. Change Management
All modifications to this standard follow the **Architecture Standard Change Process**:

1. **Proposal** – create a pull request with a clear rationale.  
2. **Impact Analysis** – list affected services and required migration steps.  
3. **Review** – Architecture Review Board (ARB) signs off.  
4. **Version Bump** – increment the document version (e.g., `v1.1`).  
5. **Publication** – merge to `main` and notify all maintainers.  

Emergency patches (critical security fixes) may bypass step 2 but still require ARB sign‑off within 24 hours.

---

## 19. Compose Exceptions
Certain services may require deviations from the baseline standard. An exception must be recorded in the service `README.md` and include the following fields:

| Field          | Description |
|----------------|-------------|
| **Reason**     | Business or technical justification for the exception. |
| **Risk**       | Potential impact on security, reliability, or compliance. |
| **Mitigation** | Controls or safeguards applied to reduce the risk. |
| **Rollback**   | Procedure to revert to a compliant state. |
| **Human Approval** | Signature of the Architecture Review Board member authorizing the exception. |

**Allowed exception categories** (non‑exhaustive):  

- DNS services (e.g., `unbound`, `coredns`)  
- VPN gateways (`wireguard`, `openvpn`)  
- Hardware passthrough (GPU, USB, PCI)  
- Host‑level monitoring agents (`node-exporter`)  
- GPU‑intensive workloads (deep‑learning containers)  
- Legacy applications requiring outdated runtime environments  

AI agents must **never** automatically “fix” a documented exception.

---

## 20. Templates
To ensure rapid onboarding and uniformity, the following template repository is provided:

- `Architecture/templates/ComposeTemplate.yaml` – skeleton compose file with all required top‑level keys in correct order.  
- `Architecture/templates/ReadmeTemplate.md` – scaffold for service documentation.  
- `Architecture/templates/.env.example` – placeholder environment file.  
- `Architecture/templates/Versions.md` – version‑tracking template.  
- `Architecture/templates/ServiceChecklist.md` – compliance checklist (mirrors §16).  

All new services must start from these templates and adapt them to the specific workload.

---

## 21. AI Decision Process
When AI agents evaluate a compose stack, they must follow the ordered decision pipeline:

1. **Schema validation** – `docker compose config` succeeds.  
2. **File presence** – required files exist.  
3. **Network/Volume verification** – referenced external resources exist.  
4. **Naming compliance** – service, container, network, and volume names follow §5.  
5. **Security checks** – non‑root user, capability drops, no host networking, secret handling.  
6. **Resource limits** – CPU/Memory limits are defined.  
7. **Healthcheck presence** – mandatory or documented exemption.  
8. **Logging policy** – driver and rotation conform to §12.  
9. **Reverse‑proxy labeling** – labels present for public services.  
10. **Exception detection** – any deviation not covered by an approved exception triggers a review flag.  

Only after passing all steps may the AI mark the stack as **Compliant**.

---

## 22. Compose Lifecycle
Compose stacks progress through defined lifecycle stages:

1. **Draft** – initial implementation, internal testing only.  
2. **Review** – undergoes Architecture Review Board audit and AI validation.  
3. **Validated** – all compliance checks pass; ready for production deployment.  
4. **Production** – actively serving traffic.  
5. **Deprecated** – superseded by a newer version; no new deployments.  
6. **Archived** – removed from active environments, retained for historical reference.

Audits are required at each transition except Draft→Review (internal) and Deprecated→Archived (automation).

---

## 23. Compliance Scoring
To provide a quantitative view of compliance, each stack receives a score:

- **100 %** – Fully compliant, all checks pass, no exceptions.  
- **≥ 95 %** – Production‑ready, minor cosmetic issues.  
- **≥ 85 %** – Minor improvements recommended (e.g., documentation tweaks).  
- **≥ 70 %** – Significant review required before production.  
- **< 70 %** – Do not deploy; fails critical checks.

The score is calculated automatically by the CI validation pipeline.

---

## Versioning Policy

This standard follows semantic document versioning.

### Major Version (v2.0)

Used for architectural or governance changes that may require updates to existing compose stacks.

### Minor Version (v1.1)

Used for new standards, clarifications, or additional guidance that do not invalidate existing compliant stacks.

### Patch Version (v1.0.1)

Used for editorial corrections, formatting improvements, typo fixes, or clarification of existing wording without changing requirements.

Every published version shall include a changelog summarizing the changes made.

---

## 24. Final Architecture Review
**Summary of changes made**  
- Removed implementation‑specific “traefik” references and introduced a generic `<proxy>` placeholder throughout the document.  
- Added explicit **Compose Exceptions**, **Templates**, **AI Decision Process**, **Compose Lifecycle**, and **Compliance Scoring** sections.  
- Generalized reverse‑proxy labeling while preserving required label structure.  
- Updated restart‑policy wording to indicate a default with documented exceptions.  
- Consolidated volume policy and clarified anonymous volume prohibition.  
- Introduced a structured exception record format.

**Architectural improvements**  
- Enhanced extensibility for future tooling (Podman, alternative reverse proxies).  
- Provided a clear governance model for AI agents and human‑approved exceptions.  
- Established a lifecycle and scoring mechanism to streamline audits.

**Remaining assumptions**  
- Host provides the core networks (`proxy`, `internal`, optional `vpn`, `gpu`).  
- SSD mount point `/monarch` and HDD/ZFS mount point `/hive` exist and are accessible.  
- Current reverse‑proxy implementation is Traefik v3 (documented in the Architecture Standard).

**Open questions**  
- Should a dedicated **monitoring network** become a core network?  
- Precise snapshot retention numbers for SSD vs. HDD (pending finalization in the Architecture Standard).

**Readiness assessment** – *Ready to freeze as Version 1.0* pending agreement on the open questions.

---

*End of Docker Compose Standard v1.0*

## Compose Standard Review
**Major decisions**
- Replaced all concrete “traefik” references with the generic `<proxy>` placeholder.
- Introduced explicit sections for Compose Exceptions, Templates, AI Decision Process, Lifecycle, and Compliance Scoring.
- Standardized reverse‑proxy labeling while keeping the implementation‑specific details in the Architecture Standard.
- Added a structured exception record format and a detailed change‑management workflow.

**Assumptions**
- Core networks (`proxy`, `internal`, optional `vpn`, `gpu`) are pre‑provisioned on the host.
- SSD mount point `/monarch` and HDD/ZFS mount point `/hive` exist and are accessible.
- The current reverse‑proxy implementation is Traefik v3, documented elsewhere.

**Open questions**
- Should a dedicated **monitoring network** be promoted to a core network?
- What are the exact snapshot‑retention policies for SSD vs. HDD storage?

**Recommendations before freezing v1.0**
1. Resolve the open questions above with the Architecture Review Board.
2. Publish the accompanying template repository (`Architecture/templates/...`) and ensure it is version‑controlled.
3. Create a CI pipeline that enforces the validation checklist and compliance scoring.
4. Obtain formal sign‑off from the Architecture Review Board and update the document version to `v1.0.1` after any minor adjustments.

*End of Docker Compose Standard v1.0*
