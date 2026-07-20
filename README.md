# homelab Repository

## Purpose
The **homelab** repository is the production‑grade governance hub for the Homelab environment.  
It houses the architecture definitions, standards, ADRs, templates, service documentation, indexes, assets, and supporting scripts that drive the long‑term operation, reliability, and scalability of the homelab.

## Scope
- **Architecture** – High‑level design decisions, networking, hardware, AI, and security diagrams.  
- **Standards** – Formal standards for documentation, Docker, security, naming, etc.  
- **ADRs** – Architecture Decision Records that capture why decisions were made.  
- **Templates** – Re‑usable compose, CI, and documentation templates.  
- **Services** – Run‑books, service‑specific documentation, and configuration artefacts.  
- **Indexes** – Auto‑generated navigation maps for services, standards, templates, ADRs, and research.  
- **Assets** – Images, diagrams, and other visual assets used across the repo.  
- **Validation** – Audit reports, benchmarks, and compliance artefacts.  
- **Scripts** – Helper scripts for maintenance, CI, and automated checks.  

## Folder Overview
```
homelab/
├─ .github/
│   └─ workflows/               # CI pipelines (future)
├─ Architecture/                # standards, decisions, diagrams, AI, hardware
├─ Assets/                      # images, icons, diagrams
├─ Validation/                  # audit reports, compliance artefacts
├─ Scripts/                     # utility scripts for CI / maintenance
├─ Templates/                   # Docker‑Compose, CI, service templates
├─ Indexes/
│   ├─ ServiceCatalog.md
│   ├─ ServiceIndex.md
│   ├─ StandardsIndex.md
│   ├─ DocumentationIndex.md
│   ├─ TemplateIndex.md
│   ├─ ADRIndex.md
│   └─ ResearchIndex.md
└─ docs/
    ├─ services/                # service run‑books
    └─ runbooks/                # operational procedures
```

## Contribution Guidelines
1. **Follow the Naming Standard** – Directories in kebab‑case, markdown files in PascalCase.md.  
2. **Front‑Matter** – Every markdown file must start with a YAML block containing `title`, `owner`, `tags`, and `lastReviewed`.  
3. **Index Updates** – After adding new artefacts, run the CI‑generated index scripts (`make indexes` or the appropriate GitHub Action) to keep navigation up‑to‑date.  
4. **Validation** – Place any audit or benchmark reports under `Validation/` and reference them in the relevant index.  
5. **Pull‑Request Checks** – CI will enforce formatting, linting, and front‑matter validation.  

## Repository Philosophy
- **Longevity** – Repository names are immutable; versioning lives inside the artefacts.  
- **Governance‑First** – Standards and ADRs drive every change; documentation is the single source of truth.  
- **Automation‑Driven** – CI pipelines automatically generate indexes, validate front‑matter, and enforce the naming standard.  
- **Modular Growth** – New domains (e.g., AI, monitoring) can be added as top‑level folders without refactoring existing structure.

## Future Roadmap
- **Automated Index Regeneration** – Full CI job that rebuilds all `Indexes/*.md` on each merge.  
- **AI‑Assisted Navigation** – Semantic search powered by the MetadataStandard to surface relevant docs.  
- **Hermes/Honcho Integration** – Impact analysis for architecture changes.  
- **Versioned Release Packages** – Exportable bundles of standards/templates for downstream consumption.

## Links to Related Repositories
- **knowledge‑base** – Research, guides, and reference material (no governance overhead).  
- **automation** – IaC, scripts, and CI/CD pipelines that provision the homelab.

---

*This README defines the foundational layout and governance model for the **homelab** repository.*