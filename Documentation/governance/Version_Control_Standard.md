---
title: Version Control Governance Standard
document_type: Standard
status: Active
version: 1.0.0
owner: Homelab Governance
applies_to: All repository contributors (human and AI)
canonical_path: Documentation/governance/Version_Control_Standard.md
---

# Version Control Governance Standard

**Canonical path:** `Documentation/governance/Version_Control_Standard.md`  
**Status:** Active  
**Version:** 1.0.0  

This document is the authoritative standard for version control, Git workflows, branching strategy, commit conventions, tagging, merge requirements, and AI-assisted development in this repository.

---

## Table of Contents

1. [Purpose](#1-purpose)
2. [Scope](#2-scope)
3. [Repository Branching Strategy](#3-repository-branching-strategy)
4. [Commit Message Standard](#4-commit-message-standard)
5. [Commit Scope Rules](#5-commit-scope-rules)
6. [Branch Completion Checklist](#6-branch-completion-checklist)
7. [Merge Readiness Checklist](#7-merge-readiness-checklist)
8. [Tagging Convention](#8-tagging-convention)
9. [AI Agent Contribution Standard](#9-ai-agent-contribution-standard)
10. [Governance Integration](#10-governance-integration)
11. [Future Evolution](#11-future-evolution)
12. [Document Control](#12-document-control)

---

## 1. Purpose

This repository follows formal Git governance so that every change remains **traceable**, **auditable**, and **repeatable**.

### 1.1 Why formal Git governance exists

Homelab repositories evolve through documentation, infrastructure, governance phases, and AI-assisted contributions. Without a shared version-control contract:

- History becomes noisy and hard to review.
- Related and unrelated work get mixed.
- Validation claims become unverifiable.
- Future contributors (human or automated) cannot reconstruct intent.

### 1.2 Goals

| Goal | Meaning |
|------|---------|
| **Traceability** | Every change can be linked to a branch, commit, phase, or review decision. |
| **Auditability** | An independent reviewer can verify what changed, why, and how it was validated. |
| **Repeatability** | Workflows produce consistent outcomes across contributors and tools. |
| **AI-assisted development** | Coding agents can contribute safely without eroding history or inventing evidence. |
| **Clean project history** | Commits and branches remain reviewable, reversible, and purposeful. |
| **Future contributor support** | New humans and agents can onboard from this standard without tribal knowledge. |

### 1.3 Design intent

This standard prefers:

- Explicit over implicit.
- Small reversible commits over large opaque ones.
- Documented validation over assumed success.
- Facts over fabricated results.

---

## 2. Scope

### 2.1 Applies to

This standard applies to **all** of the following:

| Subject | Coverage |
|---------|----------|
| Branches | All long-lived and short-lived branches |
| Contributors | All human developers and maintainers |
| AI assistants | Cursor, Cline, Claude Code, GitHub Copilot, future Brainiac / autonomous agents, and equivalent tools |
| Documentation | Standards, service docs, runbooks, validation reports, indexes |
| Infrastructure | Compose, automation, CI, host/config changes (when present in-repo) |
| Governance phases | Phase branches, QA remediations, evidence/validation work |
| Future automation | Scripts, agents, and CI jobs that create commits or branches |

### 2.2 Non-goals

This standard does **not**:

- Replace security standards for secret handling (it reinforces them).
- Define application architecture.
- Implement CI enforcement, commit linting, or branch protection (see [Future Evolution](#11-future-evolution)).
- Authorize force-pushes, history rewrites, or secret commits.

### 2.3 Precedence

When conflicts arise:

1. Security and secret-handling requirements take precedence.
2. This Version Control Standard governs Git workflow and history shape.
3. Other repository standards (documentation, Docker, ADR, naming) govern their respective domains.
4. Phase execution plans must still produce commits and branches that comply with this standard.

---

## 3. Repository Branching Strategy

### 3.1 Overview

The repository uses a **structured branching model**:

- `main` — production-ready, merge-gated history.
- `develop` — optional integration branch for multi-phase work (when used).
- Short-lived work branches for phases, features, fixes, docs, and research.

| Branch type | Naming pattern | Typical merge target |
|-------------|----------------|----------------------|
| Mainline | `main` | — (protected) |
| Integration | `develop` | `main` |
| Governance phase | `phase<major>.<minor>` (e.g. `phase9.4`) | `main` or `develop` |
| Feature | `feature/<short-kebab>` | `main` or `develop` |
| Bugfix | `bugfix/<short-kebab>` | `main` or `develop` |
| Hotfix | `hotfix/<short-kebab>` | `main` (then back-port if needed) |
| Documentation | `docs/<short-kebab>` | `main` or `develop` |
| Research | `research/<short-kebab>` | usually discarded or merged selectively |

### 3.2 Branch catalog

#### `main`

| Attribute | Rule |
|-----------|------|
| **Purpose** | Canonical, production-ready branch. Represents the agreed repository state. |
| **Lifetime** | Permanent. |
| **Merge target** | None (other branches merge into it). |
| **Naming** | Exactly `main`. |
| **Examples** | `main` |
| **Use when** | Publishing completed, reviewed, validated work. |
| **Do not use when** | Performing unfinished experiments, partial phase work, or unverified changes. |

#### `develop`

| Attribute | Rule |
|-----------|------|
| **Purpose** | Optional integration line for concurrent phases/features before release to `main`. |
| **Lifetime** | Long-lived if adopted; otherwise omit and merge phase/feature branches directly to `main`. |
| **Merge target** | `main` |
| **Naming** | Exactly `develop`. |
| **Examples** | `develop` |
| **Use when** | Multiple in-flight workstreams need a shared integration branch. |
| **Do not use when** | The repository is intentionally trunk-based with short PR cycles to `main` only. |

#### Governance phase branches (`phaseX.Y`)

| Attribute | Rule |
|-----------|------|
| **Purpose** | Isolate a governance or repository-refactor phase (inventory, documentation, evidence, QA). |
| **Lifetime** | Short-to-medium; closes when phase validation and merge readiness are complete. |
| **Merge target** | `main` (or `develop` if integration is in use). |
| **Naming** | `phase` + major + `.` + minor, no spaces. Optional suffix for remediations: `phase9.4.1`. |
| **Examples** | `phase9.4`, `phase10.1`, `phase9.4.1` |
| **Use when** | Executing a defined phase plan with validation artifacts. |
| **Do not use when** | Shipping an unrelated product feature or a one-line typo fix (use `feature/` or `docs/` / `bugfix/`). |

#### Feature branches (`feature/…`)

| Attribute | Rule |
|-----------|------|
| **Purpose** | Deliver a coherent new capability. |
| **Lifetime** | Short-lived; delete after merge. |
| **Merge target** | `main` or `develop`. |
| **Naming** | `feature/<kebab-case-description>` |
| **Examples** | `feature/docker-secrets`, `feature/n8n-monitoring` |
| **Use when** | Implementing a named capability with clear acceptance criteria. |
| **Do not use when** | Fixing a production defect urgently (`hotfix/`) or running open-ended experiments (`research/`). |

#### Bugfix branches (`bugfix/…`)

| Attribute | Rule |
|-----------|------|
| **Purpose** | Correct a known defect that is not an emergency production break-glass. |
| **Lifetime** | Short-lived; delete after merge. |
| **Merge target** | `main` or `develop`. |
| **Naming** | `bugfix/<kebab-case-description>` |
| **Examples** | `bugfix/traefik-healthchecks` |
| **Use when** | The issue is understood and scoped. |
| **Do not use when** | Exploring unknown failures without a clear fix target (`research/`) or applying an emergency production patch (`hotfix/`). |

#### Hotfix branches (`hotfix/…`)

| Attribute | Rule |
|-----------|------|
| **Purpose** | Urgent correction to `main` for broken automation, security exposure, or blocking CI. |
| **Lifetime** | Very short; merge ASAP. |
| **Merge target** | `main` (then merge/backport to active phase branches if needed). |
| **Naming** | `hotfix/<kebab-case-description>` |
| **Examples** | `hotfix/github-actions` |
| **Use when** | Production/`main` is impaired and delay is unacceptable. |
| **Do not use when** | The change is non-urgent or still speculative. |

#### Documentation branches (`docs/…`)

| Attribute | Rule |
|-----------|------|
| **Purpose** | Documentation-only changes with no infrastructure impact. |
| **Lifetime** | Short-lived; delete after merge. |
| **Merge target** | `main` or `develop`. |
| **Naming** | `docs/<kebab-case-description>` |
| **Examples** | `docs/service-catalog`, `docs/version-control-standard` |
| **Use when** | Standards, service docs, validation narrative, indexes, or runbooks change without deployable config changes. |
| **Do not use when** | The branch also modifies Compose, env, or deployment paths (use `feature/` / phase branch and separate commits). |

#### Research branches (`research/…`)

| Attribute | Rule |
|-----------|------|
| **Purpose** | Time-boxed investigation, spikes, or prototypes. |
| **Lifetime** | Short; often abandoned. |
| **Merge target** | Rarely merged whole; extract useful commits into a proper branch type. |
| **Naming** | `research/<kebab-case-description>` |
| **Examples** | `research/local-llm` |
| **Use when** | Outcome is uncertain and history may be disposable. |
| **Do not use when** | Work is already accepted as the delivery path (promote to `feature/` or phase branch). |

### 3.3 Branch naming rules

- Use lowercase letters, digits, `/`, `.`, and hyphens.
- Prefer short, descriptive suffixes.
- Do not encode secrets, hostnames with credentials, or personal data in branch names.
- One primary concern per branch.

### 3.4 Lifetime expectations

| Type | Expected lifetime |
|------|-------------------|
| `main` / `develop` | Permanent |
| Phase | Days to weeks |
| Feature / bugfix / docs | Hours to days |
| Hotfix | Hours |
| Research | Days; close or convert promptly |

---

## 4. Commit Message Standard

### 4.1 Canonical format

```text
<Phase or Type>: <Short Summary>

- Change 1
- Change 2
- Change 3

Validation
- Tests
- Verification
- Scope confirmation
```

### 4.2 Header rules

| Rule | Requirement |
|------|-------------|
| Tense | **Imperative** (“Add”, “Fix”, “Document”) — not “Added” / “Fixes” |
| Length | Concise; prefer ≤ ~72 characters for the summary line |
| Prefix | Phase id (`Phase 9.4`) **or** type (`Docs`, `Fix`, `Feature`, `Hotfix`, `Research`) |
| Clarity | Summary must stand alone in `git log --oneline` |

### 4.3 Body rules

- Use a meaningful bullet list of concrete changes.
- Prefer observable outcomes over vague process language.
- Group related bullets; do not hide infrastructure changes inside documentation bullets.

### 4.4 Validation section

Include a **Validation** section when any of the following apply:

- Governance / phase work
- Changes claiming verification, audits, or evidence updates
- Infrastructure or CI changes
- Hotfixes
- Any change where “it works” would otherwise be an unverified assertion

Minimum Validation content:

- What was checked
- Counts or commands when relevant
- Explicit scope confirmation (what was **not** modified, if important)

Omit Validation only for trivial typographical edits with no behavioral or governance impact — and prefer including it when unsure.

### 4.5 Examples

#### Governance phase

```text
Phase 9.4: Add evidence references and governance validation

- Added evidence objects to 19 service.json files
- Added Evidence References to 19 service documentation files
- Generated Phase 9.4 validation artifacts
- Completed QA remediation
- Verified documentation-only scope

Validation
- 19 service.json verified
- 20 markdown files verified
- No infrastructure modified
```

#### Infrastructure change

```text
Feature: Harden Traefik healthcheck configuration

- Added healthcheck block to Traefik compose service
- Documented expected probe endpoint in service markdown
- Updated networking troubleshooting note for failing probes

Validation
- compose config validated with docker compose config
- Healthcheck fields present in rendered service definition
- No unrelated services modified
```

#### Documentation update

```text
Docs: Add Version Control Governance Standard

- Created Documentation/governance/Version_Control_Standard.md
- Defined branching, commits, tags, merge, and AI contribution rules

Validation
- Single-file documentation change confirmed
- No infrastructure or service runtime files modified
```

#### Bug fix

```text
Fix: Correct Jellyfin documentation path references

- Replaced stale docs/services paths with Documentation/services paths
- Aligned INDEX.md link text with current directory layout

Validation
- Grep confirmed no remaining stale path strings in Jellyfin docs
- Documentation-only scope confirmed
```

#### Feature development

```text
Feature: Add n8n monitoring dashboard stubs

- Added monitoring compose overlay placeholders for n8n
- Documented required metrics endpoints in service notes

Validation
- YAML parses under docker compose config
- No secrets introduced
```

#### Hotfix

```text
Hotfix: Restore GitHub Actions checkout path

- Corrected working-directory path in CI workflow
- Re-enabled documentation validation job

Validation
- Workflow YAML linted
- Path exists in repository tree
- Change limited to .github/workflows
```

#### Research branch

```text
Research: Evaluate local LLM runtime options

- Captured comparison notes for Ollama vs llama.cpp
- Listed open questions for GPU scheduling

Validation
- Documentation-only research notes
- No production compose defaults changed
```

---

## 5. Commit Scope Rules

### 5.1 Philosophy

Commits are the **atomic unit of review and rollback**. Prefer a history that a future contributor can bisect, revert, and explain.

### 5.2 Rules

1. **One logical change per commit.**
2. **Never combine unrelated work** in the same commit.
3. **Separate documentation from infrastructure** whenever practical.
4. **Separate governance phases** into individual commits (or clearly sequenced commits within one phase branch).
5. **Avoid “misc fixes” commits.** Name the real concern.
6. **Keep commits atomic** — complete enough to stand alone after apply/revert.
7. **Ensure commits are reversible** without needing archaeology of mixed concerns.
8. **Do not commit secrets**, credentials, private keys, or live `.env` values.
9. **Do not commit temporary files**, editor swap files, or generated caches unless explicitly governed as artifacts.
10. **Do not fabricate validation results** in commit messages.

### 5.3 Good practices (examples)

| Good | Why |
|------|-----|
| Commit A: add evidence objects to `service.json`; Commit B: add Phase 9.4 validation reports | Separates data change from reporting artifacts |
| Docs-only commit on `docs/…` branch with no compose diffs | Clear blast radius |
| Hotfix commit limited to one workflow file | Easy revert |

### 5.4 Bad practices (examples)

| Bad | Why |
|-----|-----|
| “misc fixes” touching Traefik compose, 12 markdown files, and a phase report | Unrelated concerns; hard to review/revert |
| Single commit mixing Phase 9.4 evidence work with Phase 10 refactor | Breaks phase auditability |
| Commit message claims “all tests passed” with no tests run | Fabricated validation |
| Commit includes `.env` with real tokens | Secret exposure; forbidden |

### 5.5 Practical split guidance

| If the change includes… | Prefer |
|-------------------------|--------|
| Governance validation reports only | Docs/governance commit |
| `service.json` + matching service markdown for same evidence update | One logical commit (same concern) |
| Compose + docs explaining the compose change | Two commits when size/noise warrants; otherwise one tightly scoped feature commit |
| Research notes + production defaults | Split; never silently promote research into production config |

---

## 6. Branch Completion Checklist

Complete **before pushing** a branch (or before requesting review):

- [ ] Working tree matches intended scope (`git status` reviewed).
- [ ] Intended files staged; no accidental paths included.
- [ ] Verification / tests complete for the change type (when applicable).
- [ ] Validation reports updated when the branch claims governance/QA outcomes.
- [ ] Documentation updated when behavior, standards, or service metadata changed.
- [ ] No temporary files (e.g. `*.tmp`, editor backups).
- [ ] No generated caches (e.g. `__pycache__/`, `.pytest_cache/`, build outputs) unless explicitly required artifacts.
- [ ] No unrelated modifications hitchhiking on the branch.
- [ ] Repository builds / config validates correctly (when applicable).
- [ ] Commit messages follow [Section 4](#4-commit-message-standard).
- [ ] Secrets scan mindset applied (no credentials in diffs).
- [ ] Branch name matches [Section 3](#3-repository-branching-strategy).

---

## 7. Merge Readiness Checklist

Complete **before merging into `main`**:

- [ ] External review complete (human and/or designated review process).
- [ ] QA complete for the change class (phase QA, feature acceptance, or hotfix verification).
- [ ] Validation reports committed when required by the work.
- [ ] Documentation complete and consistent with code/config changes.
- [ ] No outstanding TODOs that block the claimed scope.
- [ ] Git history reviewed (`git log`, diff against base).
- [ ] Commit history is clean enough to understand (no mystery “wip” dumps without follow-up).
- [ ] Scope matches the pull request / merge description.
- [ ] No unexpected files modified.
- [ ] Branch completion checklist satisfied.
- [ ] Tagging considered if this merge closes a milestone ([Section 8](#8-tagging-convention)).
- [ ] AI-assisted changes comply with [Section 9](#9-ai-agent-contribution-standard).

### 7.1 Merge target notes

| Target | Extra expectation |
|--------|-------------------|
| `main` | Highest bar: review + validation + clean scope |
| `develop` | Integration may accept incomplete product polish, but not secret leakage or broken repo invariants |
| Phase → `main` | Phase checklist / validation artifacts present |

---

## 8. Tagging Convention

### 8.1 Purpose of tags

Tags mark **immutable milestones**: governance completion points, release candidates, and published versions.

### 8.2 Examples

| Tag | Meaning |
|-----|---------|
| `phase9.4-complete` | Governance Phase 9.4 finished and accepted |
| `phase10.0-start` | Formal start marker for Phase 10.0 |
| `v2.0.0-alpha` | Pre-release software/docs bundle |
| `v2.0.0-beta` | Feature-complete candidate pending final QA |
| `v2.0.0` | Released version |
| `release-2026-08` | Calendar/release-train milestone |

### 8.3 When to create tags

Create a tag when:

- A governance phase is completed and signed off.
- A release (or pre-release) is published.
- A known-good baseline must be referenced by automation or rollback plans.

Do **not** tag every commit or every WIP push.

### 8.4 Annotated vs lightweight

| Tag type | Use |
|----------|-----|
| **Annotated** (`git tag -a`) | **Preferred** for releases and governance milestones (includes message, author, date). |
| **Lightweight** | Acceptable for temporary local bookmarks only; avoid as the long-term record for releases. |

Example annotated tag message:

```text
Phase 9.4 complete

Evidence linkage and QA remediation accepted.
Documentation-only scope confirmed.
```

### 8.5 Governance vs release milestones

| Milestone class | Tag style | Example |
|-----------------|-----------|---------|
| Governance | `phase<id>-complete` / `phase<id>-start` | `phase9.4-complete` |
| Semantic release | `v<MAJOR>.<MINOR>.<PATCH>[-prerelease]` | `v2.0.0-rc.1` |
| Release train | `release-YYYY-MM` | `release-2026-08` |

---

## 9. AI Agent Contribution Standard

This section is **mandatory** for all AI coding assistants operating on this repository.

### 9.1 Universal rules (tool-agnostic)

AI agents **MUST**:

1. Follow this Version Control Standard.
2. Keep commits small and reviewable.
3. Use one logical change per commit.
4. Never combine unrelated work into one commit.
5. Preserve repository history.
6. Never rewrite published history unless explicitly instructed by a human maintainer.
7. Never commit secrets, credentials, private keys, or live environment values.
8. Never commit temporary files or generated caches unless they are explicit governed artifacts.
9. Include validation details in commit messages when appropriate.
10. Respect repository governance documents (standards, ADRs, validation reports, service docs).
11. Preserve auditability of phase work and evidence links.
12. Prefer documentation and cited sources over assumptions.
13. Never fabricate validation results.
14. Never fabricate evidence.
15. Clearly distinguish **facts** from **assumptions** in reports and commit text.
16. Stay within instructed path scopes (for example, documentation-only phases must not modify compose/infra).
17. Ask for clarification when merge/push/history-rewrite intent is ambiguous — default to the safer non-destructive option.

AI agents **MUST NOT**:

- Force-push to `main` (or any protected branch) unless a human explicitly orders it and policy allows.
- Use `--no-verify` to skip hooks unless explicitly instructed.
- Invent Phase validation counts, test outcomes, or evidence sources.
- Quietly expand scope “while here” into unrelated refactors.

### 9.2 Guidance by tool class

Guidance remains tool-agnostic; tool names are illustrative.

| Tool class | Expectations |
|------------|--------------|
| **Cursor** | Follow repo standards and user rules; prefer surgical diffs; do not commit unless asked; surface validation commands and results honestly. |
| **Cline** | Same commit/branch discipline; do not treat plan mode outputs as committed truth until applied and verified. |
| **Claude Code** | Preserve audit trails; avoid broad rewrites; keep phase artifacts factual. |
| **GitHub Copilot** | Suggestions must be reviewed before commit; never accept secret material into commits. |
| **Future autonomous / Brainiac agents** | Must read this standard before creating branches or commits; must emit machine-checkable validation notes; must refuse out-of-scope infra edits during documentation phases. |

### 9.3 Evidence and validation integrity

When working on governance, documentation, or AI-readiness artifacts:

- Cite only sources that exist in the repository.
- Leave evidence arrays empty when no verifiable source exists.
- Do not “improve” scores by inventing coverage.
- Record residual gaps as gaps.

### 9.4 Recommended AI commit hygiene

```text
Phase 9.4.1: Clarify AI readiness estimate and record QA artifacts

- Clarified Estimated AI Readiness Score wording
- Added duplicate Governance Metadata inventory report
- Added verification capture and QA signoff documents

Validation
- No service.json evidence content changed
- No infrastructure modified
- Verification commands captured in Phase9.4_Verification_Report.md
```

---

## 10. Governance Integration

This standard integrates with the broader repository governance system as follows:

| Domain | Integration |
|--------|-------------|
| **Repository governance** | Defines how governance phases are branched, committed, reviewed, and tagged. |
| **Documentation standards** | Documentation changes still obey documentation quality rules; this standard governs *how* those changes enter Git history. |
| **Future ADRs** | ADRs record *decisions*; this standard records *how decision artifacts are versioned*. ADR creation should use normal commit/branch rules; once ADRs exist, evidence `adrs` arrays may reference them. |
| **Validation reports** | Reports under `Validation/` are first-class artifacts: committed with the phase that produced them, referenced from commit Validation sections when relevant. |
| **Service documentation** | `Documentation/services/**` changes follow docs/phase branch rules; evidence linkage commits should remain documentation-scoped unless a phase explicitly includes runtime config. |
| **AI readiness initiatives** | Estimated readiness scores and evidence objects are audit artifacts — subject to no-fabrication rules in [Section 9](#9-ai-agent-contribution-standard). |

### 10.1 Recommended relationship to phase work

1. Open a phase branch (`phaseX.Y`).
2. Execute the phase plan with scoped commits.
3. Produce validation artifacts.
4. Complete branch and merge checklists.
5. Merge to `main` (or `develop` then `main`).
6. Tag milestone when the phase is accepted (`phaseX.Y-complete`).

---

## 11. Future Evolution

The following capabilities are **recommended future improvements**. They are **not** implemented by this document and must not be assumed present until adopted via normal change control.

| Area | Intent |
|------|--------|
| **Signed commits** | Cryptographic attribution of authors/agents. |
| **Automated changelog generation** | Derive release notes from conventional/phase commit history. |
| **Semantic versioning** | Formalize `vMAJOR.MINOR.PATCH` for repository releases. |
| **Protected branches** | Enforce review and status checks on `main` / `develop`. |
| **CI validation** | Automate schema checks, path-scope guards, and docs linting. |
| **Automated commit linting** | Mechanically verify header/body/Validation structure. |
| **Repository policy enforcement** | Server-side rules for secrets, file size, and path protections. |

Adoption of any item above should be documented (preferably via ADR) and should not silently invalidate existing phase history.

---

## 12. Document Control

| Field | Value |
|-------|-------|
| Document name | Version Control Governance Standard |
| Canonical path | `Documentation/governance/Version_Control_Standard.md` |
| Version | 1.0.0 |
| Status | Active |
| Review cadence | At least annually, or when branching/CI policy changes |
| Change process | Edit via `docs/` or phase branch; merge to `main` per this standard |

### 12.1 Amendment rules

- Amendments must themselves follow this standard.
- Breaking workflow changes should be called out explicitly in the commit Validation section.
- Do not silently weaken AI no-fabrication or secret-handling rules.

---

*End of Version Control Governance Standard*
