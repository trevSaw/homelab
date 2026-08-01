# Homelab Governance & AI Roadmap v1.1

---

# Phase 1 ✅ Homelab Architecture Standard

Establish the architectural foundation for the homelab.

## Deliverables

- Homelab Architecture Standard
- Architecture Principles
- Naming Conventions
- Network Standards
- Governance Rules
- ADR Framework

---

# Phase 2 ✅ Docker Compose Standard

Standardize every Docker deployment.

## Deliverables

- Docker Compose Standard
- Compose Structure
- Networking Rules
- Security Guidelines
- Environment Variable Standards
- Validation Requirements

---

# Phase 3 ✅ Templates

Create reusable templates for every service.

## Deliverables

- ComposeTemplate.yaml
- ReadmeTemplate.md
- .env.example
- Versions.md
- ServiceChecklist.md

---

# Phase 4 ✅ Documentation Standard

Standardize all documentation.

## Deliverables

- Documentation Standard
- Documentation Structure
- Required Documents
- AI Documentation Rules
- Cross-reference Standards
- Versioning Rules

---

# Phase 5 ✅ Service Lifecycle Standard

Define how every service moves from idea to retirement.

## Deliverables

- Service Lifecycle Standard
- Lifecycle Gates
- Ownership Matrix
- Artifact Timeline
- Validation Requirements
- Retirement Process

---

# Phase 6 ✅ Audit Standard

Create the governance and compliance framework.

## Deliverables

- Audit Standard
- Audit Methodology
- Severity Model
- Findings Schema
- Evidence Requirements
- Compliance Framework
- Continuous Improvement Loop

---

# Phase 7 ✅ AI Governance Standard

Define how AI participates in the homelab.

## Deliverables

- AI Governance Standard
- AI Roles
- AI Workflow
- Capability Matrix
- Decision Matrix
- Escalation Matrix
- Quality Gates
- Prompt Governance
- Memory Governance
- AI Metrics
- AI Maturity Model

---

# Phase 8 ✅ Repository Refactor

Rebuild the repository so it reflects the governance standards.

## Goals

- Standardize folder hierarchy
- Organize documentation
- Consolidate standards
- Organize templates
- Build indexes
- Build service catalog
- Organize ADR repository
- Create archive structure
- Ensure every document has a defined location

## Deliverables

- Repository v2 Structure
- Standards Index
- Service Catalog
- Service Index
- ADR Repository
- Documentation Index
- Template Library
- Archive Layout

---

# Phase 9 ✅ Repository Governance & AI Readiness

**Status:** ✅ Complete  

**Completed:** 2026-07-23  

**Close-out report:** [`Validation/Phase9/Phase9_Completion_Report.md`](../../Validation/Phase9/Phase9_Completion_Report.md)

Apply the governance framework to every service in the homelab.

Every service ultimately follows the same governance pipeline:

```text
Inventory
        ↓
Current State Assessment
        ↓
Architecture Review
        ↓
Documentation Review
        ↓
Compose Review
        ↓
Networking Review
        ↓
Storage Review
        ↓
Secrets Review
        ↓
Security Hardening
        ↓
Audit
        ↓
Validation
        ↓
Deploy Readiness
```

## Phase 9 Outcomes

- Service inventory and classification (19 services)
- AI-ready service documentation + `service.json` metadata
- Evidence linkage to Phase 9.1 sources
- Governance validation and independent QA
- Estimated AI Readiness Score: **96 / 100**
- Technical debt / future improvements registered for Phase 10

---

# Phase 9.1 ✅ Service Inventory & Planning

**Status:** ✅ Complete  

Build the authoritative inventory of every service before any refactoring begins.

## Objectives

- Discover every service
- Verify service ownership
- Categorize services
- Identify dependencies
- Determine migration priority
- Define implementation waves

## Deliverables

- Master Service Inventory
- Service Classification Matrix
- Dependency Map
- Runtime Configuration Inventory
- Risk Register
- Migration Priority Matrix
- Migration Wave Plan
- Phase 9 Execution Plan

---

# Phase 9.2 ✅ Service Documentation Framework

**Status:** ✅ Complete  

Create standardized, AI-consumable service documentation and metadata for every inventoried service.

## Objectives

- Standardize service documentation
- Create structured service metadata (`service.json`)
- Build AI-consumable documentation
- Capture governance metadata
- Prepare services for future implementation work

## Deliverables

- 19 service directories under `Documentation/services/`
- Service markdown + `service.json` for each service
- Services `INDEX.md`
- Phase 9.2 governance and validation reports

---

# Phase 9.3 ✅ Governance Audit & Evidence Traceability

**Status:** ✅ Complete  

## Objectives

- Validate repository governance
- Assess schema validity of service metadata
- Measure evidence traceability
- Assess AI readiness (baseline)
- Confirm no secret exposure / infrastructure drift from docs work

## Deliverables

- Phase 9.3 Combined / Governance Audit Reports
- Schema Validation Report
- Evidence Traceability Report
- Secret Exposure & Infrastructure Drift Reports
- Phase 9.3 Final Checklist
- Baseline Estimated AI Readiness: **85 / 100**

---

# Phase 9.4 ✅ Evidence Linkage & AI Readiness

**Status:** ✅ Complete  

## Objectives

- Link verifiable Phase 9.1 evidence to every service
- Raise Estimated AI Readiness to ≥ 95
- Record technical debt
- Perform independent QA review (Phase 9.4.1)

## Deliverables

- Evidence objects on 19 `service.json` files
- Evidence References in 19 service markdown files
- Phase 9.4 validation artifacts (`Validation/Phase9.4/`)
- Phase 9.4.1 QA signoff (**PASS**)
- Estimated AI Readiness: **96 / 100**
- Phase 9 Completion Report (`Validation/Phase9/Phase9_Completion_Report.md`)

---

# Phase 10 — Infrastructure Standardization & Service Modernization

**Status:** ✅ Complete (scoped) — 2026-07-29  
**Branch:** `phase10`  
**Host:** mocha (Ubuntu 22.04 LTS)

Scoped Phase 10 delivered backwards-compatible compose standardization, secret hygiene, script modernization, energy-audit improvements, documentation sync, and validation tooling.

**Explicitly deferred** (see `Validation/Phase10/Remaining_Risks.md`):

- Storage layout migrations
- Networking topology changes / host-port removal
- Service renames / image pinning campaigns
- Full DockerStandard directory-layout migration (`compose/<domain>/...`)
- Phase 9.4 future items F10-1 through F10-6 (governance metadata enrichment)

Implement the governance standards established during Phase 9 across the live homelab environment **without redesigning running infrastructure**.

This phase transforms the repository from a governed design into a production-standard personal infrastructure baseline for the scoped deliverables above.

## Objectives

- Standardize production compose files where safe (logging, restart, healthchecks, resources)
- Eliminate plaintext secrets from tracked compose files
- Modernize operational scripts
- Improve energy audit reporting
- Synchronize documentation with implementation
- Provide local validation tooling and Phase 10 QA artefacts

---

## Scope

### Docker Standardization (completed — incremental)

Bring every deployment into safer compliance with the Docker Compose Standard **without** changing application behavior, storage mounts, service names, or network topology.

Implementation includes:

- Logging rotation (`max-size: 10m`, `max-file: 3`)
- Restart policy normalization (`unless-stopped`)
- Health checks where obvious and safe
- Conservative `deploy.resources` limits (generous; skipped where risk of breakage)
- Removal of obsolete commented-out compose blocks
- `.env` / `.env.example` for secrets

### Storage Modernization

**Deferred.** No bind-mount or dataset migrations in Phase 10.

### Networking Modernization

**Deferred.** Host ports and networks left unchanged.

### Security Hardening (partial)

- Remove plaintext secrets from compose (ollama, beszel_agent, hermes, code-server, authentic)
- `.gitignore` enforces `.env` exclusion
- Privileged containers / Docker socket exposure reviewed but not redesigned

### Technical Debt Resolution (partial)

- Script strict-mode modernization
- Energy audit bugfixes and reporting improvements
- Documentation synchronization
- Remaining items documented in Phase 10 remaining risks

---

## Deliverables

- Updated Docker Compose deployments under `Services/`
- `.env.example` templates for secret-bearing services
- `Scripts/validate.sh`
- Energy audit v1.4 + docs
- `Validation/Phase10/` QA pack

---

## Validation Criteria

- Compose files validate successfully (or warn on missing local `.env` off-host)
- Secrets managed via env files / interpolation (not plaintext in Git)
- Documentation reflects production-safe Phase 10 scope
- Deferred work explicitly recorded

---

## Exit Criteria

Scoped Phase 10 is complete when:

- Safe compose standardization applied across active `Services/` stacks
- Known plaintext secrets removed from tracked compose files
- Scripts under `Scripts/` use modern bash practices where touched
- Energy audit v1.4 features verified and docs synced
- Validation tooling and Phase 10 QA artefacts exist
- Deferred roadmap items are documented (not silently marked done)

---

# Phase 10.9 — Production Stabilization & Baseline

**Status:** 🟡 Planned

Create the last known-good production baseline before making structural changes.

## Purpose

Establish a recoverable, documented production snapshot of the live homelab after scoped Phase 10, so subsequent storage, security, and AI work proceeds from a verified known-good state.

## Deliverables

- Git synchronization
- Production inventory
- Validation artifacts
- Backup verification
- Restore testing
- Baseline documentation

---

# Phase 11 — Storage Modernization

**Status:** ✅ Complete with Deferred Items (2026-07-31)

Modernize production storage layout, including migration of workloads and data related to `/hive` → `/mnt/monarch`.

## Deliverables

- AppData migration — **core Phase 10.5 hive wave complete**
- Media separation — **complete**
- Backup redesign — **deferred**
- Storage standards — **complete** (`services.conf` + framework)
- Compose updates — **complete for cut-over services**
- Validation — **complete**

See `Validation/Phase11/Phase11_Final_Status.md` and `Phase11_Remaining_Work.md`.

---

# Phase 12.1 — Production Compose Standardization Pilot

**Status:** ✅ Complete (2026-07-31)

Implement the finalized Docker deployment standard on a small production pilot group (Traefik, Portainer, Beszel, Uptime Kuma). Establishes the canonical pattern for later cutovers — **not** a full-fleet migration.

## Deliverables

- Compose standardization (repo SoT, pinned images, health/restart/resources) — **done**
- Appdata storage for pilot configs — **done** (Uptime Kuma migrated; others already on appdata)
- `.env.example` + secrets out of compose — **done**
- Documented security exceptions — **done**
- Per-service validation under `Validation/Phase12.1/` — **done**
- Pilot completion report under `Documentation/Phase12.1/` — **done**

See `Documentation/Phase12.1/Phase12.1_Completion_Report.md`.

---

# Phase 12.2A — Media Download Infrastructure

**Status:** ✅ Complete (2026-07-31)

Apply Phase 12.1 compose pattern to download clients: **qBittorrent (Hotio)** and **NZBGet**. SABnzbd is not used on this host and was excluded.

## Deliverables

- Pinned images + repo SoT under `services/Hotio` and `services/NZBget` — **done**
- App config remains `/mnt/monarch/appdata/{hotio,nzbget}`; downloads stay on `/hive` — **done**
- `.env.example` + healthchecks + resource limits — **done**
- VPN / shared-netns exceptions documented — **done**
- Validation under `Validation/Phase12.2A/` — **done**

See `Documentation/Phase12.2A/Phase12.2A_Completion_Report.md`.

**Explicitly not in this phase:** Sonarr, Radarr, Jellyfin, media libraries, SABnzbd, qBittorrent 5.x.

---

# Phase 12.2B — Sonarr Migration

**Status:** ✅ Complete (2026-07-31)

Migrate native systemd/mono Sonarr (`/var/lib/sonarr`) into Phase 12 Docker SoT at `services/sonarr/` with appdata on `/mnt/monarch/appdata/sonarr`. Abandoned `/hive/Hotio/sonarr` was not used.

## Deliverables

- Pinned image `lscr.io/linuxserver/sonarr:version-3.0.10.1566` — **done**
- State copy preserving 214 series + config/DB — **done**
- Host-network exception for localhost download clients — **documented**
- Validation under `Validation/Phase12.2B/sonarr/` — **done**
- Rollback procedure — **done**

See `Documentation/Phase12.2B/Phase12.2B_Completion_Report.md`.

**Explicitly not in this phase:** Radarr, Bazarr, Lidarr, Jellyfin, media moves, Sonarr v4 upgrade.

---

# Phase 12.2C — Radarr Migration & Network Remediation

**Status:** ✅ Complete (2026-07-31)

Migrate Radarr to Phase 12 SoT (`services/radarr/`, `/mnt/monarch/appdata/radarr`), dual-home `proxy`+`hotio`, and fix download-client FAIL (self-IP → Docker DNS `qbittorrent`).

See `Documentation/Phase12.2C/Phase12.2C_Completion_Report.md`.

**Explicitly not in this phase:** Sonarr re-home, Prowlarr, Jellyfin, Bazarr, Lidarr, downloaders, media moves.

---

# Phase 12.2D — Prowlarr Migration & Platform Standardization

**Status:** ✅ Complete (2026-07-31)

Migrate Prowlarr to Phase 12 SoT (`services/prowlarr/`, `/mnt/monarch/appdata/prowlarr`), dual-home `proxy`+`hotio`, Traefik labels, remediate Radarr app URLs to Docker DNS.

See `Documentation/Phase12.2D/Phase12.2D_Completion_Report.md`.

**Explicitly not in this phase:** Sonarr re-home, Jellyfin, Jellyseerr, Bazarr, Lidarr, downloaders, media moves.

---

# Phase 12 — Media Stack Networking Standard

**Status:** ✅ Documented (2026-07-31)

Canonical dual-network model for the full media platform: `proxy` (Traefik/Authentik ingress) + `hotio` / live `hotio_default` (automation DNS). Dual-homed: Sonarr, Radarr, Prowlarr (+ Bazarr/Lidarr when deployed). Proxy-only: Traefik, Jellyfin, Overseerr. Hotio-only: qBittorrent, NZBGet.

See `Architecture/media-stack-networking.md` (amended membership is authoritative). **No live cutovers in this deliverable** — future Phase 12 media migrations must comply.

---

# Phase 12.3 — Media Platform Validation

**Status:** ✅ Complete (2026-07-31)

Read-only validation of the media **automation** platform (qBittorrent, NZBGet, Sonarr, Radarr, Prowlarr) as a single system after 12.2A–12.2D.

**Verdict:** PASS WITH DOCUMENTED EXCEPTIONS (primary debt: Sonarr host networking).

See `Documentation/Phase12.3/Platform_Validation_Report.md`.

---

# Phase 12.4 — Media Consumption Platform Standardization

**Status:** ✅ Complete (2026-07-31)

Standardize Jellyfin, Jellyseerr, and Bazarr to Phase 12 SoT (proxy / dual-home as required, Traefik, Monarch appdata, pinned images). Lidarr not deployed (OOS). Automation stack not modified.

See `Documentation/Phase12.4/Phase12.4_Completion_Report.md`.

---

# Phase 12.5 — Production Baseline & Phase Closeout

**Status:** ✅ Complete (2026-07-31)

Read-only final audit. Publishes the authoritative production baseline, technical debt, deferred work, and acceptance signoff. **No production changes.**

See `Documentation/Phase12.5/Phase12_Final_Report.md` and `Production_Baseline.md`.

---

# Phase 12 — COMPLETE

**Status:** ✅ COMPLETE (2026-07-31)

Phase 12 delivered production Docker standards across core infrastructure, media automation, and media consumption, plus the media networking architecture and closeout baseline.

**Approved remaining debt:** `Documentation/Phase12.5/Technical_Debt.md`  
**Deferred beyond Phase 12:** `Documentation/Phase12.5/Deferred_Work.md`  
**Phase 13 starts from:** `Documentation/Phase12.5/Production_Baseline.md`

> Note: The following “Phase 12 — Secrets & Security” section is a **separately planned security track** (historical roadmap naming). It is **not** part of the completed Phase 12 media/infrastructure program above.

---

# Phase 12 — Secrets & Security

**Status:** 🟡 Planned

Complete security modernization deferred or only partially addressed during Phase 10.

## Deliverables

- Docker Secrets
- Vault
- Secret rotation
- Network hardening
- Container hardening
- Security validation

---

# Phase 13 — AI Architecture & Knowledge Platform (Brainiac / KORA)

**Status:** 🚧 IN PROGRESS (started 2026-08-01)

Phase 13 shifts the project from infrastructure standardization toward the construction of the AI platform that will operate on top of the homelab. The focus becomes architecture, orchestration, memory, knowledge management, and intelligent services while preserving the stable production baseline established during Phase 12.

**Prerequisite / starting point:** `Documentation/Phase12.5/Production_Baseline.md`  
**Authoritative working roadmap:** `Documentation/Phase13/Phase13_Roadmap.md`  
**Do not regress:** Phase 12 media `proxy`/`hotio` fabric or Monarch appdata conventions without an explicit change.

AI learns and operates on an already-governed personal homelab platform rather than creating one. Architecture precedes implementation.

### Governance Requirement

Phase 13 SHALL conform to the existing Homelab Governance Framework. No new governance standards shall be introduced unless approved through an ADR. All Docker Compose files, directory layouts, documentation, validation artifacts, architecture documents, service definitions, naming conventions, deployment patterns, and future implementations SHALL comply with the governance standards already established within the Homelab repository. In the event of a conflict, the Homelab Governance Framework SHALL take precedence unless explicitly superseded by an approved ADR.

---

# Phase 13.0 — KORA Architecture Alignment

**Status:** ✅ Complete (2026-08-01)

Align AI architecture documentation to the finalized model: **KORA is Brainiac**; KORA is a Council member and Conductor / First Among Equals; Memory, Knowledge, Tools, Agents, and Models are separated concerns.

See `Architecture/ai/KORA.md` and `Documentation/Phase13/KORA_Architecture_Alignment.md`.

---

# Phase 13.1 — Council Architecture

**Status:** ✅ Complete (2026-08-01)

Define the Council as the reasoning framework used by KORA, including selection, deliberation lifecycle, deliberative synthesis, conceptual schemas, and prompt architecture.

## Deliverables

- Council directory structure
- Council architecture
- Dynamics.md
- Member specifications
- Selection rules
- Voting / deliberative synthesis rules
- Deliberation lifecycle
- Prompt architecture
- Conceptual schemas
- Canonical member template

See `Architecture/ai/Council/` and `Documentation/Phase13/Council_Operational_Model.md`.

---

# Phase 13.2 — Knowledge Architecture

**Status:** ✅ Complete (2026-08-01)

Define how KORA organizes, retrieves, governs, and supplies reference information to Council reasoning. Memory remains a separate system; runtime memory/knowledge implementation is Phase 13.5.

## Deliverables

- `Architecture/ai/Knowledge.md`
- Knowledge domains, lifecycle, quality model, retrieval, governance, conceptual relationships
- Memory ≠ Knowledge boundary clarified
- `Documentation/Phase13/Knowledge_Architecture_Model.md`

---

# Phase 13.3 — Agent Orchestration

**Status:** ✅ Complete (2026-08-01)

Define how KORA delegates temporary execution work through agents without conflating agents with Council members. No framework or runtime selection in this phase.

## Deliverables

- `Architecture/ai/Agents.md`
- Agent lifecycle, creation rules, boundaries, permissions, types
- Explicit Council ≠ Agents model
- `Documentation/Phase13/Agent_Architecture_Model.md`

---

# Phase 13.4 — External Integrations

**Status:** ✅ Complete (2026-08-01)

Define how KORA safely interacts with external systems through a governed tool layer and conceptual MCP protocol architecture. No MCP servers or integrations are deployed in this phase.

## Deliverables

- `Architecture/ai/Tools.md`
- Expanded `Architecture/ai/MCP.md`
- Tool lifecycle, permissions, safety, truth model, governance
- `Documentation/Phase13/Tool_Architecture_Model.md`

---

# Phase 13.5 — Knowledge & Memory Runtime

**Status:** ✅ Complete (2026-08-01)

Define memory runtime, knowledge runtime evolution/promotion, and context assembly architecture. No databases, embeddings, or retrieval systems are deployed in this phase.

## Deliverables

- `Architecture/ai/Memory_Runtime.md`
- `Architecture/ai/Knowledge_Runtime.md`
- `Architecture/ai/Context_Assembly.md`
- `Documentation/Phase13/Memory_Runtime_Model.md`

---

# Phase 13.6 — User Experience

**Status:** ✅ Complete (2026-08-01)

Define the KORA user experience contract: interaction patterns, Council visibility modes, memory/knowledge UX, and explainability without raw chain-of-thought. No UI frameworks or clients are selected in this phase.

## Deliverables

- `Architecture/ai/User_Experience.md`
- `Architecture/ai/Interaction_Model.md`
- `Architecture/ai/Explainability.md`
- `Documentation/Phase13/User_Experience_Model.md`

---

# Phase 13.7 — Implementation Architecture Framework

**Status:** ✅ Complete (2026-08-01)

Define implementation layers, deployment philosophy, and technology evaluation methodology so future selections cannot redefine KORA. Candidates (Honcho, Graphify, ChromaDB, Hermes, Open WebUI) are evaluation targets only—not adopted by this phase.

## Deliverables

- `Architecture/ai/Implementation_Architecture.md`
- `Architecture/ai/Technology_Evaluation_ADR_Template.md`
- `Documentation/Phase13/Implementation_Architecture_Model.md`

---

# Phase 13.8 — Technology Evaluation & Adoption ADRs

**Status:** ✅ Complete (2026-08-01)

Evaluate first-wave candidates (Hermes, Open WebUI, Honcho, ChromaDB, Graphify) against KORA contracts. Evaluation and adoption posture only—no installs or production stack finalization.

## Deliverables

- `Architecture/decisions/ADR-0004`–`ADR-0008`
- `Architecture/decisions/ADRIndex.md` (updated)
- `Documentation/Phase13/Technology_Evaluation_ADR_Model.md`

---

# Phase 13.9 — KORA Thin Vertical Slice Architecture

**Status:** ✅ Complete (2026-08-01)

Define the minimum end-to-end KORA workflow, prototype boundaries, and conceptual integration flow. Architecture validation only—no installs or compose.

## Deliverables

- `Architecture/ai/Vertical_Slice.md`
- `Architecture/ai/Prototype_Boundaries.md`
- `Architecture/ai/Integration_Flow.md`
- `Documentation/Phase13/Vertical_Slice_Model.md`

---

# Phase 13.10 — KORA Prototype Spike Architecture

**Status:** ✅ Complete (2026-08-01)

Define the first controlled non-production spike as planning only: architecture, acceptance criteria, and test plan. Does not authorize runtime, compose, installs, or infrastructure changes.

## Deliverables

- `Architecture/ai/Spike_Architecture.md`
- `Architecture/ai/Spike_Acceptance_Criteria.md`
- `Architecture/ai/Spike_Test_Plan.md`
- `Documentation/Phase13/Prototype_Spike_Model.md`

---

# Phase 13.11 — KORA Runtime Spike Execution

**Status:** ✅ Complete (2026-08-01)

Execute disposable non-production runtime spike under `/mnt/monarch/prototypes/kora-spike/`. Repository receives documentation and validation artifacts only—no production deployment.

## Deliverables

- `Architecture/ai/Runtime_Spike_Execution.md`
- `Documentation/Phase13/Runtime_Spike_Report.md`
- `Validation/Phase13.11/`

---

# Phase 13.12 — Context Intelligence Architecture

**Status:** ✅ Complete (2026-08-01)

Define classification-aware retrieval intelligence, strategies, and ranking between Classification and Context Assembly. Architecture only—no runtime or Docker.

## Deliverables

- `Architecture/ai/Context_Intelligence.md`
- `Architecture/ai/Retrieval_Strategies.md`
- `Architecture/ai/Context_Ranking.md`
- `Documentation/Phase13/Context_Intelligence_Model.md`

---

# Phase 13.13 — Context Intelligence Runtime Validation

**Status:** ✅ Complete (2026-08-01)

Implement and validate classification-driven retrieval, ranking, budgets, and explainability in the isolated non-production KORA spike. Runtime remains outside Git; repository receives documentation and validation only.

## Deliverables

- `Architecture/ai/Context_Intelligence_Validation.md`
- `Documentation/Phase13/Context_Intelligence_Runtime_Report.md`
- `Validation/Phase13.13/`

**Result:** 10/10 scenarios passed; Phase 13.11 preference over-fetch eliminated.

---

# Phase 13.14 — Runtime Profiles & Runtime Contracts

**Status:** ✅ Complete (2026-08-01)

Define Solo / Simulated / Distributed / Hybrid runtime profiles plus behavioral contracts, observability requirements, and state ownership. Architecture only—no production deployment.

## Deliverables

- `Architecture/ai/Runtime_Profiles.md`
- `Architecture/ai/Runtime_Contracts.md`
- `Architecture/ai/Runtime_Observability.md`
- `Architecture/ai/Runtime_State.md`
- `Documentation/Phase13/Runtime_Profile_Model.md`

**Sequence:** 13.14 → 13.15 Production Implementation Architecture → Phase 14 Production Runtime Implementation.

---

# Phase 13.15 — Production Implementation Architecture

**Status:** ✅ Complete (2026-08-01)

Define production topology, logical service cards, staged rollout, and operational readiness for KORA. Docker Compose is the planned Phase 14 substrate—not created in this phase.

## Deliverables

- `Architecture/ai/Production_Architecture.md`
- `Architecture/ai/Deployment_Topology.md`
- `Architecture/ai/Production_Service_Topology.md`
- `Architecture/ai/Rollout_Strategy.md`
- `Architecture/ai/Operational_Readiness.md`
- `Documentation/Phase13/Production_Architecture_Model.md`
- `Validation/Phase13.15/`

**Boundary:** Phase 13 architecture complete. Phase 14 begins implementation.

---

# Phase 14 — KORA Production Runtime Implementation

**Status:** 🟡 In Progress (14.1 complete)

**Primary Goal:** Implement KORA production runtime in staged slices without rewriting Phase 13 architecture.

Implement Phase 13 architecture as production runtime (Docker Compose substrate) in staged slices. Does not rewrite Phase 13 contracts.

**Working roadmap:** `Documentation/Phase14/Phase14_Roadmap.md`

## Sub-phases

| Sub-phase | Title | Status |
| --- | --- | --- |
| 14.1 | Runtime Foundation (KORA + Hermes + Open WebUI + Ollama) | ✅ Complete (2026-08-01) |
| 14.2 | Memory Runtime | Planned |
| 14.3 | Knowledge Runtime (RAG) | Planned |
| 14.4 | Context Assembly Engine | Planned |
| 14.5 | Tool & MCP Runtime | Planned |
| 14.6 | Council Integration | Planned |
| 14.7 | Autonomous Workflows & Agent Orchestration | Planned |

## Constraints

- Solo Runtime is the initial production profile
- KORA remains product identity; Hermes/Open WebUI/Ollama are substrates
- Memory ≠ Knowledge; Council ≠ Agents; Tools ≠ Decisions
- Graphify deferred; Obsidian external only
- Phase 12 baseline preserved unless explicitly changed

## Goal

Ship a governed KORA production path before broader homelab AI automation.

---

# Phase 15 — AI Automation

**Status:** 🟡 Planned

Gradually automate homelab operations while preserving human governance. Begins after Phase 14 foundation (14.1–14.7) is stable.

## Automation Targets

- Automatic documentation
- ADR generation
- Compliance reviews
- Service creation
- Health monitoring
- Self-healing suggestions
- Pull request generation
- Change planning
- Automatic audits
- Change proposals
- Lifecycle management
- Scheduled compliance reviews
- Template generation
- Service reviews
- Architecture validation
- Compliance reporting
- Knowledge reuse
- Continuous improvement

## Human Approval Required

- Homelab service deployments
- Architecture changes
- Security decisions
- Breaking changes
- Governance changes

## Goal

AI becomes a governance assistant—not a governance replacement.

---

# Long-Term Vision

```text
Governance
        ↓
Repository Standardization
        ↓
Infrastructure Standardization
        ↓
Production Stabilization
        ↓
Storage Modernization
        ↓
Security Modernization
        ↓
AI Architecture & Knowledge Platform (Brainiac / KORA)
        ↓
Council · Memory · Orchestration · MCP · UX
        ↓
KORA Production Runtime (Phase 14)
        ↓
AI Automation (Phase 15+)
        ↓
Continuous Improvement
```