# Service Deployment Checklist
<!-- Derived from Docker Compose Standard v1.0 -->

## Directory Layout
- [ ] Service folder contains `compose.yaml`, `.env.example`, `README.md`, `Versions.md`
- [ ] `config/`, `data/`, `media/` (if applicable), and `scripts/` directories are present as needed

## Compose Compliance
- [ ] `compose.yaml` follows the exact ordering defined in the standard
- [ ] All optional sections are either present with proper comments or fully omitted

## Naming
- [ ] Service name, container name, and hostname use lower‑case hyphen‑separated format
- [ ] Volume, network, and environment variable names follow the conventions

## Networks
- [ ] At least one core network (`internal`, `proxy`, `vpn`, `gpu`) is attached
- [ ] No undeclared custom networks are defined

## Volumes
- [ ] All persistent data uses bind mounts to approved storage locations
- [ ] No anonymous Docker volumes are used

## Environment Variables
- [ ] `.env.example` exists and lists all required variables
- [ ] `.env` is git‑ignored and not committed
- [ ] No plaintext secrets appear in version‑controlled files

## Security
- [ ] `user:` is set to a non‑root UID/GID where possible
- [ ] Unnecessary Linux capabilities are dropped
- [ ] `read_only:` is used for configuration mounts when feasible
- [ ] No `privileged: true`, `network_mode: host`, `pid: host`, or `ipc: host` unless documented exception

## Resources
- [ ] CPU and memory limits are defined under `deploy.resources.limits`
- [ ] Reservations are defined (optional, future‑proof)
- [ ] GPU devices are listed only if required and documented

## Healthchecks
- [ ] Healthcheck block is present (or documented exemption)

## Logging
- [ ] Logging driver and rotation options are defined

## Documentation
- [ ] `README.md` includes all required sections (overview, installation, backup, etc.)
- [ ] `Versions.md` tracks image tags and upgrade notes
- [ ] Exception documentation is present if any deviation exists

## Exceptions
- [ ] Reason for any deviation from the Docker Compose Standard is documented
- [ ] Risk assessment for the deviation is provided
- [ ] Mitigation steps are described
- [ ] Rollback plan is outlined
- [ ] Human (ARB) approval signature is recorded

## Validation
- [ ] `docker compose config` succeeds without errors
- [ ] All referenced external networks and volumes exist on the host
- [ ] Images are pinned (no `latest` tags)

## Lifecycle
- [ ] Service is categorized (Draft, Review, Validated, Production, Deprecated, Archived) as per the Architecture Standard

## Architecture Review
- [ ] ARB sign‑off is recorded (link or signature) in `README.md` or `Versions.md`

## Final Approval
- [ ] All checklist items are satisfied
- [ ] Release manager has approved deployment