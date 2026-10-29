# Homelab Obsidian Architecture v1

**Status:** Active
**Version:** 1.0.0
**Owner:** Homelab (single administrator)
**Canonical path:** `Documentation/ObsidianHomelabArchitecture.md`

This document defines the **personal homelab Obsidian knowledge architecture v1**. It is the governance and design document for the Obsidian vault that models the homelab as a long-lived technical knowledge graph.

> **Filename note:** The task referenced `Documentation/obsidian-homelab-architecture.md`. Per the repository's `NamingConventionStandard.md` (Markdown files use PascalCase), this document is named `ObsidianHomelabArchitecture.md`. The reference files in `Documentation/references/` retain their original lowercase filenames to preserve their content-identity (they were moved verbatim).

---

## 1. Purpose

The homelab Obsidian vault answers, as a navigable knowledge graph:

- What services exist?
- How do services relate to one another?
- Why was a particular architectural decision made?
- Which phase introduced a capability?
- What is currently active / planned / retired?
- How do I operate or troubleshoot something?
- What infrastructure depends on something else?
- What research informed a decision?
- Where are the canonical technical documents?
- Which notes are derived versus authoritative?

This is a **maintainable system**, not a collection of random Markdown files. It is explicitly **not** the infrastructure source of truth.

## 2. Design Principles

1. **Repository is canonical.** The `homelab` Git repository is the source of truth for infrastructure configuration, service documentation, ADRs, phases, and standards. The vault is a **derived** knowledge layer that references the repository.
2. **Separate concerns.** Three distinct systems that must not be conflated:
   - `homelab` Git repository → canonical infrastructure/documentation source.
   - Obsidian vault → personal knowledge-management / derived knowledge graph.
   - CouchDB → Obsidian LiveSync synchronization backend (never a vault; never a working vault filesystem).
3. **No second infrastructure source of truth.** The vault never silently becomes authoritative for infrastructure configuration.
4. **One note, one purpose.** Each note models one entity (service, phase, ADR, guide, etc.).
5. **Properties for structure, tags for classification, Wikilinks for relationships.** Avoid redundant duplication across these mechanisms.
6. **Controlled vocabulary.** Domains, tags, statuses, phases, and note types are governed and validated — never invented ad hoc.
7. **No invented facts.** Never invent services, phases, statuses, architecture, dependencies, or decisions. Use real repository evidence.
8. **Simple, explicit, reproducible, inspectable, governed.**

## 3. Folder Structure

The vault lives at **`/mnt/monarch/obsidian-vault/`** (external to the repo, separate from `/mnt/monarch/appdata/couchdb/`).

```
obsidian-vault/
├── Home.md                  # Homepage target; top-level navigation
├── Inbox/                   # landing zone only (new notes / imports)
├── Architecture/            # type: architecture
├── Services/                # type: service
├── Phases/                  # type: phase
├── ADRs/                    # type: adr
├── Guides/                  # type: guide
├── Troubleshooting/         # type: troubleshooting
├── Research/                # type: research
├── MOCs/                    # navigation surfaces (type: moc)
│   ├── Architecture.md
│   ├── Services.md
│   ├── Phases.md
│   ├── ADRs.md
│   ├── Guides.md
│   ├── Troubleshooting.md
│   └── Research.md
├── Templates/               # one template per approved note type
└── Settings/
    └── tags.md              # controlled tag vocabulary
```

Avoid deeply nested folders; flat per-type folders provide real organizational benefit.

## 4. Note Types

| Type | Purpose | Maps to (canonical) | Template |
|------|---------|---------------------|----------|
| `service` | A deployed, planned, or retired homelab service | `services/<name>/`, `Documentation/services/`, `Services/ServiceIndex.md` | `Templates/Service.md` |
| `architecture` | How the system works (networking, split-horizon DNS, AI, storage) | `Architecture/` | `Templates/Architecture.md` |
| `phase` | An implementation phase (12.1–19) | `Documentation/PhaseXX/`, `Documentation/Phases/` | `Templates/Phase.md` |
| `adr` | An Architecture Decision Record | `Architecture/decisions/ADR-####-*.md` | `Templates/ADR.md` |
| `guide` | A how-to / runbook | `Documentation/runbooks/` | `Templates/Guide.md` |
| `troubleshooting` | Problem → cause → resolution | `Documentation/troubleshooting/` | `Templates/Troubleshooting.md` |
| `research` | Research that informed a decision | ServiceIndex (research/watching items) | `Templates/Research.md` |
| `moc` | Navigation surface (Map of Content) | derived, not canonical | `Templates/MOC.md` |

**`project` type: REJECTED.** The homelab organizes work by **phases**, not projects. Planned initiatives are captured as `service` notes with `status: planned` and a `phase`. No separate `project` type in v1.

## 5. YAML / Property Schema

Vault notes use their **own** schema, distinct from the repository's `document_type/owner/version` schema, because the vault is external and derived.

Common properties (all notes):

```yaml
---
type: <note type>            # from approved note types
name: <Human Readable Name>
status: <planned|active|deprecated|retired>   # DERIVED classification
phase: <string | list>       # real phase value(s), never invented
domain:                      # from approved domain vocabulary
  - <domain>
tags:                        # from Settings/tags.md
  - <tag>
canonical_source: <repo path> # path in homelab repo (when one exists)
canonical_status: <exact canonical value>   # only when collapsed (see §6)
---
```

Service notes additionally may use:

```yaml
technologies:                # currently-active technologies only
  - <tech>
historical_technologies:     # retired/replaced technologies (context only)
  - <tech>
```

Link fields (frontmatter) where relationships are needed (Wikilinks are preferred for narrative):

```yaml
depends_on: [ ... ]
related_services: [ ... ]
governed_by: [ ... ]
documented_by: [ ... ]
informed_by: [ ... ]
supersedes: [ ... ]
```

Rules:
- Keep properties predictable; avoid duplicate information.
- Do not encode everything as tags.
- Use properties for structured metadata; tags for lightweight classification; Wikilinks for relationships.
- Do not create a property when a Wikilink is more appropriate.

### Domain vocabulary (14, each justified by repo evidence)

| # | Domain | Evidence |
|---|--------|----------|
| 1 | `infrastructure` | HomelabArchitectureStandard; ServiceIndex (portainer, homepage, cosmoos, couchdb) |
| 2 | `networking` | `Architecture/networking/`; Technitium; Traefik |
| 3 | `dns` | `Architecture/networking/DNS.md`; Technitium/Pi-hole split-horizon work |
| 4 | `storage` | HomelabArchitectureStandard storage domain; ZFS; `Storage_Architecture.md`; appdata |
| 5 | `security` | `SecurityStandard.md`; Phase 18 `.env` audit |
| 6 | `identity` | authentic/authentik SSO; `Validation/Identity_Audit_Pre_Phase10.5.md` |
| 7 | `ai` | `Architecture/ai/`; ollama, kora, hermes, open-webui, chromadb, graphify, honcho |
| 8 | `monitoring` | beszel, uptime-kuma; HomelabArchitectureStandard "Monitoring" |
| 9 | `automation` | n8n, homeassistant, `scripts/` |
| 10 | `media` | jellyfin, jellyseerr, sonarr, radarr, prowlarr, bazarr, etc. |
| 11 | `productivity` | nextcloud, calibre-web, actual, sparkyfitness |
| 12 | `development` | code-server |
| 13 | `backup` | `BackupStandard.md`; `scripts/backup/` |
| 14 | `utilities` | ServiceIndex "Utilities" category (NZBget, EchoOS, byparr) |

(`observability` → `monitoring`; `applications` → media/productivity/development; `homelab` and `documentation` rejected as redundant.)

### Technology vocabulary

Active technologies (lowercase kebab) derived from `services/` and `Services/ServiceIndex.md`: `docker`, `docker-compose`, `traefik`, `technitium`, `tailscale`, `zfs`, `couchdb`, `obsidian`, `ollama`, `hermes`, `kora`, `open-webui`, `chromadb`, `graphify`, `honcho`, `n8n`, `homeassistant`, `jellyfin`, `nextcloud`, `portainer`, `uptime-kuma`, `beszel`, `mariadb`, `authentic`, `wireguard`, `proxmox`, `code-server`, `nzbget`, `homepage`, `calibre-web`, `actual`, `sparkyfitness`, `crafty`, `kavita`, `byparr`, `echoos`, `cosmoos`, and the *arr stack (`sonarr`, `radarr`, `prowlarr`, `bazarr`, `jellyseerr`, `lazylibrarian`, `readarr`, `kavita`).

**Historical/retired technologies** (e.g., `pi-hole`) are NOT listed under `technologies` on active notes; they appear only under `historical_technologies` or in historical notes, clearly labeled.

## 6. Status: Derived Classification

Obsidian `status` is a **derived** classification. The repository's `Services/ServiceIndex.md` status vocabulary and the Service Lifecycle Standard remain **canonical** and are never modified to fit the vault.

Deterministic mapping (canonical → derived):

| Canonical status | Derived `status` | `canonical_status` recorded? |
|------------------|------------------|------------------------------|
| Production | `active` | no (equivalent) |
| Testing | `active` | yes: `Testing` |
| Planned | `planned` | no (equivalent) |
| Researching | `planned` | yes: `Researching` |
| Watching | `planned` | yes: `Watching` |
| Rejected | `retired` | yes: `Rejected` |
| Replaced | `deprecated` | yes: `Replaced` |
| Archived | `retired` | yes: `Archived` |

**Rule:** Whenever collapsing multiple canonical states would create meaningful ambiguity, the exact canonical value is preserved in `canonical_status`. The validator enforces that `status` is one of the four derived values.

## 7. Tag Taxonomy

Tags are **lightweight classification**, governed by `Settings/tags.md` (one per line, no `#`). Do **not** auto-generate `#phase-19`, `#status-active`, or `#type-service` — those are properties.

Approved v1 tags (documented in `Settings/tags.md`):

```
split-horizon
dns
reverse-proxy
zfs
storage
secrets
security-hardening
migration
retirement
ai-orchestration
memory
knowledge
observability
backup
sso
automation
media
productivity
development
utilities
infrastructure
```
> Tag list is authoritative in `Settings/tags.md`. This list is a summary; the file is the source of truth.

## 8. Wikilink / Relationship Rules

The vault behaves like a knowledge graph via Wikilinks. Conventions:

- `[[Service Name]]` — link to a service note.
- `[[Phase 19]]` — link to a phase note.
- `[[ADR-0004]]` — link to an ADR note.
- `[[Traefik]]`, `[[Technitium DNS]]` — link by entity name.

Useful relationships:

- Service → deployed during → Phase
- Service → depends on → Service (`depends_on`)
- Service → documented by → Guide (`documented_by`)
- Service → governed by → ADR (`governed_by`)
- ADR → supersedes → ADR (`supersedes`)
- Research → informed → ADR (`informed_by`)
- Troubleshooting → concerns → Service
- Project → implements → Architecture

Do not create fake relational metadata when a normal Wikilink is sufficient.

## 9. MOC Architecture

MOCs are **navigation surfaces**, not duplicated databases. They use Dataview where appropriate. All MOCs set `AutoNoteMover: disable`.

| MOC | Purpose |
|-----|---------|
| `Home.md` | Root; links all MOCs; Homepage target |
| `MOCs/Architecture.md` | Architecture + ADR navigation |
| `MOCs/Services.md` | Active services dashboard + service list |
| `MOCs/Phases.md` | Phase overview |
| `MOCs/ADRs.md` | Recent ADRs |
| `MOCs/Guides.md` | Guides index |
| `MOCs/Troubleshooting.md` | Troubleshooting index |
| `MOCs/Research.md` | Research index |

## 10. Canonical vs Derived Information

### Canonical (authoritative, in the repository)
- Repository documentation (`Architecture/`, `Documentation/`)
- ADRs (`Architecture/decisions/`)
- Phase reports (`Documentation/PhaseXX/`)
- Actual Compose configuration (`services/<name>/compose.yaml`)
- Authoritative service configuration (`services/`)
- Service Lifecycle Standard and ServiceIndex statuses

### Derived (in the vault)
- Obsidian service summaries
- Dataview dashboards and automatically generated indexes
- AI-generated classifications
- Relationship summaries
- `canonical_status` (derived from canonical status)

**Boundary:** The vault references the repository via `canonical_source` and never silently becomes the authoritative source for infrastructure configuration. Never modify canonical repository content to fit the vault schema.

## 11. OpenCode Responsibilities

**OpenCode MAY:**
- Import existing documentation (copy-first).
- Understand source documents.
- Split large documents where appropriate.
- Determine note type.
- Create structured frontmatter.
- Create Wikilinks.
- Create/update MOCs.
- Identify relationships.
- Preserve original meaning.
- Identify canonical vs derived content.
- Validate generated notes.

**OpenCode MUST NOT:**
- Invent infrastructure, phases, service states, or architecture.
- Silently rewrite authoritative documentation.
- Create unsupported tags.
- Modify canonical repository content to fit the vault schema.

## 12. AI Tagger Universe Responsibilities

- Classify/enrich notes (from the controlled vocabulary).
- Apply controlled topic tags.
- Preserve existing valid tags.
- Use the approved vocabulary.
- Avoid inventing arbitrary tags.

AI Tagger does **not** define the entire ontology.

## 13. Auto Note Mover Responsibilities

- File notes based on approved routing rules (Inbox → approved destinations).
- Does **not** determine architecture, semantics, or taxonomy.
- Does **not** rewrite content.
- Does **not** create new taxonomy.

## 14. Dataview Responsibilities

- Query structured properties.
- Build dashboards.
- Generate service/phase/status views.
- Reduce manual index maintenance.

## 15. Homepage Responsibilities

- Provide navigation.
- Current system overview.
- Useful dashboards.
- Entry points into architecture/services/phases.
- Opens `Home.md` on startup.

Not a giant manually maintained document.

## 16. Local AI Responsibilities

- Tagging via AI Tagger Universe (local Ollama).
- Avoid multiple competing local AI plugins for the same task.
- Avoid unnecessary model load.
- Respect homelab AI governance.
- Never bypass governance or rewrite canonical content.

## 17. Automation Boundaries

| Tool | May touch | Excluded |
|------|-----------|----------|
| AI Tagger | `Inbox/` only | `Templates/`, `MOCs/`, `Settings/`, `Services/`, `Architecture/`, `ADRs/`, `Phases/`, `Guides/`, `Troubleshooting/`, `Research/` |
| Auto Note Mover | `Inbox/` → approved destinations | `Templates/`, `MOCs/`, `Settings/`, and all filed folders |
| Dataview | read-only queries | — |
| Homepage | opens `Home.md` | — |

Automation must not endlessly reclassify already-organized knowledge.

## 18. Tag / Vocabulary Governance

`Settings/tags.md` is the source of truth (one tag per line, no `#`). New tags are added to the file **and** to this document before use. Use Tag Wrangler to merge invented tags into the controlled set.

## 19. Templates

Templates exist for each approved note type (in `Templates/`):

- `Templates/Service.md`
- `Templates/Architecture.md`
- `Templates/Phase.md`
- `Templates/ADR.md`
- `Templates/Guide.md`
- `Templates/Troubleshooting.md`
- `Templates/Research.md`
- `Templates/MOC.md`

Templates contain valid YAML, stable properties, encourage Wikilinks, avoid invented values, and make the intended purpose obvious. Templates are excluded from automation.

## 20. Dataview Dashboards

Justified v1 dashboards (in the relevant MOCs):

- **Active Services** (Services MOC): service, status, phase, domain, technologies.
- **Phase Overview** (Phases MOC): phase, status, associated services.
- **Recent ADRs** (ADRs MOC): ADR, date, status, affected services.
- **Troubleshooting Index** (Troubleshooting MOC): service, problem, resolution, date.
- **Guides Index** (Guides MOC): guide, service, phase.
- **Research Index** (Research MOC): research, service, status.

Only dashboards with real utility are created.

## 21. Import / Migration Workflow

1. Copy rather than destroy the source.
2. Determine whether the source is canonical or derived.
3. Determine note type.
4. Add valid frontmatter.
5. Add appropriate Wikilinks.
6. Preserve original meaning.
7. Do not invent missing information.
8. Add to `Inbox/` staging.
9. Validate before automation.
10. Update MOCs only after notes are valid.

Never import: secrets, credentials, private keys, `.env` contents, temporary files, backups, generated garbage, or vendor documentation that is not owned homelab documentation.

## 22. Validation Rules

Run `scripts/obsidian/validate_vault.py` (read-only on the repo; operates on the vault path as a separate system). Checks:

- YAML parses (malformed YAML flagged).
- `type` is an approved note type.
- `status` is an approved derived status.
- `domain` ⊆ approved domains.
- `tags` ⊆ `Settings/tags.md` vocabulary.
- `phase` references real phases.
- `canonical_source` paths exist where present.
- No duplicate note identities.
- No invalid/unknown Wikilinks where detectable.
- No secrets/credentials/`.env` patterns.
- No unexpected files in controlled directories (`Templates/`, `Settings/`, `MOCs/`).
- Retired technologies not listed as active `technologies` on active services.

The validator never mutates canonical repository documentation.

## 23. Known Limitations

- v1 does not bulk-import existing homelab documentation; only 3 exemplar notes exist.
- Plugin configuration (`.obsidian/`) is documented but not installed.
- Some Wikilinks to not-yet-created notes are intentionally unresolved (they resolve as notes are added).
- Dataview dashboards require the community Dataview plugin (documented, not installed).

## 24. Future Extensions

- Controlled migration of existing service/ADR/phase documentation into the vault.
- Automated index regeneration aligned with repository indexes.
- Hermes/Honcho integration for impact analysis.
- Semantic search (Smart Connections) with a small embed model.
- Additional dashboards as the note graph grows.

## 25. Version History

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-08-20 | Initial Homelab Obsidian Architecture v1 |
