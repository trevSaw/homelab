---
title: Homelab Documentation Standard
document_type: Standard
owner: Documentation Team
status: Draft
version: 1.0.0
---
# Purpose

Define a unified, implementation‑agnostic set of principles and rules that govern **all** documentation produced for the homelab. The standard ensures documentation is **human readable**, **AI friendly**, **consistent**, **searchable**, **maintainable**, and **future‑proof**.

# Scope

Applies to every documentation artifact created for the homelab, including but not limited to:

- README files  
- Architecture documents  
- Standards  
- Audit reports  
- Runbooks  
- Troubleshooting guides  
- Upgrade procedures  
- Migration documentation  
- Architecture Decision Records (ADR)  
- Project documentation  
- Service documentation  
- Infrastructure documentation  
- Disaster Recovery documentation  

The standard does **not** prescribe implementation‑specific details (e.g., container runtimes, cloud providers).

# Document Hierarchy

```
Homelab/
├─ Architecture/
│  ├─ Architecture/standards/
│  ├─ HomelabArchitectureStandard.md
│  ├─ DockerStandard.md
│  └─ DocumentationStandard.md
├─ Architecture/templates/
│  ├─ ReadmeTemplate.md
│  ├─ ADRTemplate.md
│  └─ ... (other templates)
├─ services/
│  └─ <service‑name>/
│     ├─ README.md
│     ├─ runbook.md
│     └─ …
└─ audits/
   └─ …
```

Higher‑level standards outrank lower‑level artifacts (see *Document Precedence*).

# Documentation Philosophy

1. **Documentation is source code** – lives in version control, reviewed, and versioned.  
2. **Explain WHY before HOW** – context precedes procedure.  
3. **Survive personnel changes** – clear, explicit, self‑contained.  
4. **Minimize tribal knowledge** – capture decisions, rationales, and processes.  
5. **Human + AI readable** – plain language, consistent structure, searchable metadata.  
6. **Avoid implementation duplication** – reference standards instead of copying them.  
7. **Single source of truth** – each fact appears once; updates propagate via references.  
8. **Evolve through version control** – never edit a published copy without a commit.

# Documentation Principles

* **MUST** be stored in the repository alongside code/configuration.  
* **SHALL** include the metadata block defined in *Document Metadata*.  
* **SHOULD** use the Markdown conventions defined in *Markdown Standards*.  
* **MAY** embed diagrams, tables, and code blocks when they add clarity.  
* **MUST NOT** contain contradictory or outdated information.  
* **MUST** be reviewed at least annually or when a related standard changes.

# Naming Standards

* Directories: lowercase kebab-case, except the top-level `Architecture/` directory.
* Markdown files: PascalCase with `.md`; `README.md` is the standard index exception.
* ADRs: `ADR-0001-ShortTitle.md` in `Architecture/homelab/decisions/`.
* Standards: PascalCase files in `Architecture/standards/`, such as `DocumentationStandard.md`.
* Templates: PascalCase Markdown or descriptive configuration names in `Architecture/templates/`.

# Directory Organization

| Directory                | Purpose                                    |
|--------------------------|--------------------------------------------|
| `Architecture/`          | Standards, architecture docs, decisions.    |
| `Architecture/templates/` | Markdown/YAML templates referenced by docs.|
| `homelab/docs/services/` | Service-specific documentation. |
| `homelab/docs/runbooks/` | Operational procedures. |
| `homelab/docs/troubleshooting/` | Known issues and fixes. |
| `homelab/audit/`         | Audit and compliance reports.             |

All directories must contain a `README.md` that briefly describes its purpose.

# Required Documentation

Every service must have at least:

- A **README** (service overview).  
- An **ADR** for any architecture‑affecting decision.  
- A **Runbook** for operational procedures.  

Optional artifacts (audit, migration, disaster‑recovery) are created per the *Documentation Classification* table.

# Documentation Classification

| Document Type       | Purpose                                 | Creation Trigger                    | Owner               | Required | Template                    | Expected Lifecycle |
|---------------------|------------------------------------------|--------------------------------------|---------------------|----------|-----------------------------|--------------------|
| README              | Service overview & quick start           | Service creation or major update      | Document Owner      | Yes      | `ReadmeTemplate.md`        | Draft → Review → Approved → Published |
| ADR                | Architecture decision record            | Architectural change requiring justification | Document Owner      | Yes      | `ADRTemplate.md`           | Draft → Review → Approved → Published |
| Standard           | Governance and engineering standards    | New governance need or revision       | Standard Owner      | Yes      | `StandardTemplate.md`      | Draft → Review → Approved → Published |
| Runbook            | Operational procedures                   | New service deployment or operational change | Document Owner      | Optional | `RunbookTemplate.md`       | Draft → Review → Approved → Published |
| Audit              | Compliance and validation reports       | Periodic compliance audit or post‑incident review | Document Owner      | Optional | `AuditTemplate.md`         | Draft → Review → Approved → Published |
| Troubleshooting    | Known issues & resolutions               | Incident occurrence or recurring issue | Document Owner      | Optional | `TroubleshootingTemplate.md`| Draft → Review → Approved → Published |
| Migration          | Service migration procedures            | Service migration planning            | Document Owner      | Optional | `MigrationTemplate.md`     | Draft → Review → Approved → Published |
| Disaster Recovery  | Recovery steps for critical services    | Critical service design or risk assessment | Document Owner      | Required for critical services | `DRTemplate.md`           | Draft → Review → Approved → Published |
| Template           | Boilerplate files for other docs        | Creation of new document type          | Template Owner      | –        | –                           | Draft → Review → Approved → Published |

**For each type** define purpose, creation trigger, maintainer, mandatory/optional status, template reference, and expected lifecycle (draft → review → active → deprecated).

# Document Metadata

All Markdown documents shall start with a YAML front‑matter block:

```yaml
---
title: <Human readable title>
document_type: <README|ADR|Standard|Runbook|Audit|…>
service: <service‑name or “Homelab”>          # optional
owner: <team or individual>
status: <Draft|Active|Deprecated>
lifecycle: <Active|Retired>                  # optional
version: <semver>
last_reviewed: <YYYY‑MM‑DD>                  # optional
related_documents:
  - <Document title>                         # optional
---
```

* **Required fields**: `title`, `document_type`, `owner`, `status`, `version`.  
* **Optional fields**: `service`, `lifecycle`, `last_reviewed`, `related_documents`.  

Metadata must be updated whenever the document’s purpose, owner, or version changes.

# Document Structure

1. **Title** (in metadata & first H1)  
2. **Purpose** – why the document exists.  
3. **Scope** – what is covered.  
4. **Body** – organized per the document type (see *README Standard*, *ADR*, *Runbook*, etc.).  
5. **Versioning** – version line in metadata and optional change log at end.

# Markdown Standards

* **Headings** – use ATX (`#`, `##`, …) with a single space after the hashes.  
* **Lists** – unordered lists with `-` and ordered lists with `1.`. Indent two spaces for sub‑items.  
* **Tables** – pipe‑separated, header row separated by `---`. Align with colons if needed.  
* **Callouts** – use blockquotes with a leading emoji for notes/warnings, e.g., `> ⚠️ Warning:`.  
* **Code blocks** – fenced with triple backticks, specify language identifier.  
* **Horizontal rules** – `---` on its own line, surrounded by blank lines.  
* **Spacing** – blank line before and after headings, lists, tables, and code blocks.  
* **Line length** – wrap prose at 120 characters.  
* **File & folder names** – kebab‑case, lower‑case, no spaces.

# Writing Style

* Concise, technical, free of marketing fluff.  
* Explain **WHY** before **HOW**.  
* Use active voice.  
* Prefer nouns over adjectives.  
* Use RFC‑style terminology (`MUST`, `SHALL`, `SHOULD`, `MAY`).  
* Avoid ambiguous language.

# Headings

| Level | Markdown | Use |
|-------|----------|-----|
| H1 | `#` | Document title (single per file) |
| H2 | `##` | Major sections (e.g., Purpose, Scope) |
| H3 | `###` | Sub‑sections (e.g., Naming Standards) |
| H4 | `####` | Detailed items within a sub‑section |

# Tables

* Use pipe syntax.  
* Header row must be present.  
* Align columns as needed.

# Code Blocks

```markdown
```language
// code here
```
```

* Always include language identifier for syntax highlighting.  
* For shell scripts, use `bash`.  
* For configuration files, use `yaml` or appropriate.

# Images and Diagrams

* Store images in `docs/assets/` or a service‑specific `assets/` folder.  
* Reference with relative paths: `![](../assets/diagram.png)`.  
* Prefer SVG for scalability; PNG/JPG when raster is required.  
* Provide alt‑text for accessibility.

# Links and Cross References

* Internal links: `[Section Title](#section-title)` (lower‑case, hyphens).  
* Cross‑document links: `[Homelab Architecture Standard](../Architecture/Homelab%20Architecture%20Standard%20v1.0.md)`.  
* Always reference **document titles** not file names alone.

# Versioning

Use semantic versioning (MAJOR.MINOR.PATCH) in the `version` metadata field.

* **MAJOR** – structural or policy changes.  
* **MINOR** – additive, backward‑compatible changes.  
* **PATCH** – typo fixes, minor wording edits.

Every published version **must** include a *Version History / Changelog* section documenting the changes.

# Change Management

1. Create a branch `doc/standard/vX.Y.Z`.  
2. Update the document and bump the version.  
3. Submit a Pull Request labeled `doc‑standard`.  
4. Review by **Reviewer**.  
5. Approve by **Approver** → merge → tag `vX.Y.Z`.

# Architecture Decision Records (ADR)

* Stored under `Architecture/Decisions/`.  
* Must include: **Title**, **Status**, **Context**, **Decision**, **Consequences**, **Metadata** (see *Document Metadata*).  
* Reference ADRs from any related document via `[[ADR-001 – Title]]`.

# Service Documentation Requirements

* **README** – purpose, quick start, required ports, health checks, links to runbooks/ADRs.  
* **Runbook** – startup, shutdown, scaling, troubleshooting steps.

# Infrastructure Documentation Requirements

* High‑level diagram (plantuml, mermaid).  
* Network topology, storage layout, dependency graph.  
* Reference to *Homelab Architecture Standard* for naming and topology rules.

# Runbook Requirements

* Preconditions, step‑by‑step procedures, expected outcomes, rollback steps, responsible owner.

# Audit Documentation Requirements

* Scope, methodology, findings, remediation actions, reviewer, date, version.

# Troubleshooting Documentation

* Symptom, cause, resolution, related ADR/Runbook, escalation path.

# Upgrade Documentation

* Pre‑upgrade checklist, backup requirements, upgrade steps, post‑upgrade validation, rollback plan.

# Disaster Recovery Documentation

* Recovery Time Objective (RTO), Recovery Point Objective (RPO), step‑wise restoration, required assets, contact information.

# Templates

Reference the files in `Architecture/templates/`:

* `ReadmeTemplate.md` – service README scaffold.  
* `ADRTemplate.md` – ADR scaffold.  
* `RunbookTemplate.md` – operational runbook scaffold.  
* `AuditTemplate.md` – audit report scaffold.  
* `DRTemplate.md` – disaster recovery scaffold.  

Do **not** copy template content; simply link to them.

# AI Documentation Rules

## AI May

* Reformat markdown, fix grammar, improve readability.  
* Reorder sections to improve flow (respecting required order).  
* Add missing metadata if absent.  
* Generate missing documentation from templates when prompted.  
* Update links to reflect renamed files.

## AI Must Not

* Change architectural decisions or requirements.  
* Delete or alter ADRs, standards, or governance documents without explicit human approval.  
* Modify the *Documentation Standard* itself.  
* Remove or rename required fields in metadata.

## AI Must Escalate

* Conflicting standards.  
* Architectural changes.  
* ADR modifications.  
* Governance changes.  
* Missing required documentation.  
* Conflicting documentation.  
* Template changes affecting standards.  
* If a requested modification would change the purpose, scope, authority, governance, or architectural intent of a document, the AI must escalate for human review.

# AI Decision Process

When an AI agent identifies a need to modify documentation:

1. **Assess Impact** – determine whether the change affects architecture, governance, or mandatory policy.  
2. **Check Authorization** – verify that the requested change is within the AI May scope.  
3. **Escalate if Needed** – if the change falls under *AI Must Escalate*, create a ticket or comment for human review before proceeding.  
4. **Apply Allowed Changes** – perform transformations that are permitted (formatting, grammar, metadata additions, link updates).  
5. **Log the Action** – record the change in a comment on the pull request with a brief description of what was altered and why.  
6. **Request Review** – after applying allowed changes, request a human reviewer to validate the result.

This process ensures AI‑driven edits remain safe, auditable, and aligned with governance.

# Definition of Done

A document is **Done** when **all** items in the checklist below are satisfied:

- [ ] Metadata block present and accurate.  
- [ ] All required sections (as per document type) are present and ordered.  
- [ ] Conforms to *Markdown Standards* and *Writing Style*.  
- [ ] Passes spell‑check and lint (e.g., `markdownlint`).  
- [ ] Reviewed and approved by the designated **Reviewer** and **Approver**.  
- [ ] Merged to `main` with proper version tag and changelog entry.

# Exceptions

* Emergency patches (e.g., critical security fix) may skip the full review process but must be followed by a post‑mortem review within 48 hours.

# Compliance

* Documentation must be auditable via Git history.  
* Non‑compliant docs are flagged during CI with `markdownlint` and a custom linter that checks for required metadata fields.  
* Documentation must maintain a single source of truth; duplicate information is prohibited.

# Lifecycle

| Phase      | Purpose                                            | Entry Criteria                              | Exit Criteria                                 | Responsible Role |
|------------|----------------------------------------------------|--------------------------------------------|-----------------------------------------------|-----------------|
| Draft      | Initial authoring and internal review.            | Author creates document, status = Draft.  | Document reviewed and approved for next phase.| Document Owner |
| Review     | Peer review and feedback incorporation.           | Status = Draft, Reviewer assigned.        | All review comments addressed, status updated. | Reviewer |
| Approved   | Formal approval before publication.                | Reviewer sign‑off, Approver assigned.      | Approver signs off, status = Approved.        | Approver |
| Published  | Publication to the main branch with version tag.  | Status = Approved, version bump performed.| Merged to main, tag created, status = Published.| Standard Owner |
| Deprecated | Marking outdated documents for removal or archiving.| New version released, old document outdated.| Status changed to Deprecated, reference updated.| Standard Owner |
| Archived   | Final archiving of superseded documents.           | Document is Deprecated for >12 months.    | Moved to archive folder, status = Archived.   | Standard Owner |

# Appendices

*Appendix A – Glossary*  

| Term | Definition |
|------|------------|
| **ADR** | Architecture Decision Record – a documented decision. |
| **RTO** | Recovery Time Objective. |
| **RPO** | Recovery Point Objective. |
| **AI** | Artificial Intelligence agents that assist with documentation. |

*Appendix B – Example Metadata Block*  

```yaml
---
title: "Example Service README"
document_type: README
service: example-service
owner: platform-team
status: Active
version: 1.2.0
last_reviewed: 2026-07-01
related_documents:
  - "Example Service ADR-001"
---
```

# Governance Roles

The following roles are referenced throughout this standard. Use the exact titles:

- **Architecture Owner** – owns the Homelab Architecture Standard.  
- **Standard Owner** – maintains this Documentation Standard.  
- **Template Owner** – responsible for the creation and upkeep of templates.  
- **Document Owner** – author/maintainer of an individual document.  
- **Reviewer** – performs peer review of changes.  
- **Approver** – gives final sign‑off before a version is published.

# Documentation Relationships

* **Narrative references** – *Document Title → Section Name* (e.g., *Homelab Architecture Standard → Network Topology*). These establish authority and context.  
* **Hyperlinks** – Markdown relative links used solely for navigation (e.g., `[Architecture Standard](../Architecture/Homelab%20Architecture%20Standard%20v1.0.md)`).  

Narrative references define which document is authoritative; hyperlinks simply aid readers.

# Document Precedence

Higher‑level documents define requirements; lower‑level documents implement them. In case of conflict, the higher‑level document is authoritative.

- **Homelab Architecture Standard** – foundational architectural constraints.  
- **Docker Compose Standard** – defines container orchestration conventions used by services.  
- **Homelab Documentation Standard** – governs documentation practices and metadata.  
- **Templates** – provide structured scaffolds for concrete artifacts.  
- **Architecture Decision Records (ADR)** – capture and communicate architectural decisions.  
- **README** – service overview and quick start information.  
- **Runbook** – operational procedures for services.  
- **Audit** – compliance and validation reports.  
- **Service Documentation** – specific documentation per service (READMEs, runbooks, etc.).  
- **Disaster Recovery Documentation** – recovery procedures for critical services.

# Documentation Auditing

An AI audit agent can use the following checklist:

- [ ] Verify required metadata fields are present.  
- [ ] Detect broken relative links.  
- [ ] Identify orphaned documents (no references).  
- [ ] Find duplicate information across documents.  
- [ ] Flag stale documentation (no review within 12 months).  
- [ ] Ensure all required sections exist for the document type.  
- [ ] Confirm ADR references are present where needed.  
- [ ] Validate compliance with referenced standards.  
- [ ] Cross‑reference validation (narrative references resolve).

The audit does **not** prescribe a concrete implementation; it defines the scope for future AI audit agents.