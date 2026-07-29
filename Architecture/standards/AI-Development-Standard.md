# AI Development Standard v1.0

---

## 1. AI Development Philosophy

The homelab adopts a philosophy that AI **augments** human decision‑making rather than replaces it. The following principles **MUST** be adhered to:

- **Human Oversight** – All substantive architectural, security, and production decisions **SHALL** receive explicit human approval before being enacted.
- **Consistency First** – AI shall prioritize consistency with existing standards and codebases before proposing novel solutions.
- **Reference Over Duplication** – When generating artifacts, AI **SHALL** reuse existing components, libraries, or documentation wherever feasible.
- **Auditable Trail** – Every AI‑generated change **MUST** be recorded in an immutable audit log that references the originating request, inputs, and decisions.
- **Technical Debt Minimisation** – AI shall favour patterns that reduce future maintenance burden and shall flag any introduced technical debt for human review.
- **Continuous Documentation** – Documentation updates **SHALL** be produced concurrently with code changes and **MUST** reference the relevant sections of the Documentation Standard.

These principles are independent of any specific LLM, vendor, or tooling.

---

## 2. AI Capability Matrix

| Role | Primary Responsibilities | Allowed Actions | Approval Required | Escalation Required |
|------|--------------------------|----------------|-------------------|----------------------|
| Planner AI | Gather requirements, produce high‑level plans | Create planning artifacts, suggest timelines | No (unless plan affects production) | Yes, if plan conflicts with existing Architecture Standard |
| Builder AI | Generate code, configurations, and infrastructure manifests | Write implementation files, propose commits | Yes – Architecture approval, Security review where applicable | Yes, if generated artifacts violate standards |
| Reviewer AI | Perform self‑review of Builder output | Add review comments, suggest improvements | No (self‑review) | Yes, if reviewer finds violations of critical standards |
| Auditor AI | Validate compliance with Documentation, Service Lifecycle, and Audit standards | Run automated checks, produce audit reports | No (audit report is advisory) | Yes, when audit flags high‑severity issues |
| Memory AI | Retrieve and surface prior decisions, ADRs, and historical context | Provide context snippets, reference past decisions | No | No |
| Orchestrator AI | Coordinate hand‑offs between agents, track state machine | Update task status, trigger next stage | No | Yes, if orchestration state diverges from defined workflow |
| Human Operator | Final authority on all gated activities | Approve/reject proposals, intervene on escalations | N/A | N/A |

---

## 3. AI Workflow

The complete lifecycle for any AI‑assisted task is defined below. Each stage **SHALL** reference the appropriate existing standards.

| Stage | Purpose | Inputs | Outputs | Responsible AI Role | Required Standards | Human Approval | Escalation Conditions |
|------|---------|--------|---------|-------------------|-------------------|----------------|-----------------------|
| **Idea** | Capture a raw concept or request. | Request description, stakeholder input. | Idea brief (markdown). | Planner AI | — | No | If idea conflicts with business policy. |
| **Planning** | Produce a structured plan, tasks, and timelines. | Idea brief, existing architecture docs. | Detailed plan document. | Planner AI | Documentation Standard → Section 2 | No (unless plan affects production architecture). | Architecture conflict. |
| **Architecture Review** | Validate that the proposed architecture complies with Homelab Architecture Standard. | Plan document. | Signed architecture review record. | Auditor AI (assisted by Human) | Homelab Architecture Standard → Section 3 | **MUST** obtain Human approval. | Critical violations. |
| **Implementation Planning** | Break the approved architecture into concrete implementation steps. | Architecture review record. | Implementation plan (tasks, dependencies). | Orchestrator AI | Service Lifecycle Standard v1.0 → Section 4 | No | Dependency dead‑lock. |
| **Development** | Generate source code, configuration, and scripts. | Implementation plan. | Code commits, CI artifacts. | Builder AI | Documentation Standard → Section 2, Service Lifecycle Standard v1.0 → Section 5 | Yes – Architecture and Security approvals. | Lint or test failures. |
| **Validation** | Run automated tests, static analysis, and compliance checks. | Code commits. | Test reports, compliance verdict. | Builder AI (with Auditor AI verification) | Service Lifecycle Standard v1.0 → Section 6 | No (but must pass). | Test failures > threshold. |
| **Documentation** | Produce or update service docs, ADRs, and user guides. | Validated code, implementation plan. | Updated documentation artifacts. | Memory AI (assisted by Builder AI) | Documentation Standard → Section 3 | No | Missing required sections. |
| **Audit** | Perform a formal audit of the complete change set. | All artifacts from previous stages. | Audit report, mitigation actions. | Auditor AI | Audit Standard Implementation Plan → Section 3 | No (audit is advisory) | High‑severity audit findings. |
| **Deployment** | Deploy to target environment following approved procedures. | Approved code, configuration, documentation. | Running service, deployment logs. | Orchestrator AI (Human oversight) | Service Lifecycle Standard v1.0 → Section 7 | **MUST** obtain Human deployment approval. | Deployment rollback required. |
| **Maintenance** | Ongoing updates, bug fixes, and performance tuning. | Deployed service, monitoring data. | Maintenance tickets, patches. | Builder AI & Planner AI | Documentation Standard → Section 4 | No | Repeated failures. |
| **Continuous Improvement** | Incorporate audit lessons, update templates, and refine prompts. | Audit findings, user feedback. | Revised standards, updated templates. | Memory AI & Orchestrator AI | — | No | None (homelab-local). |

---

## 4. AI Decision Matrix

| Decision Context | AI Action | Human Override |
|------------------|-----------|----------------|
| **Approve** | AI may automatically approve low‑risk items that fall within pre‑approved limits. | Human **MUST** be able to override at any time. |
| **Suggest** | AI may propose alternatives or optimisations. | Human **SHALL** accept or reject. |
| **Modify** | AI may modify existing artifacts if they pass all automated checks. | Human approval **MUST** be recorded for critical changes. |
| **Create** | AI may create new files/components under defined templates. | Human **MUST** sign‑off when creation impacts production or security. |
| **Delete** | AI may delete deprecated artifacts only after audit clearance. | Human **MUST** approve deletion of any production asset. |
| **Escalate** | AI escalates when it detects violations of any mandatory standard. | Human **SHALL** investigate the escalation. |
| **Reject** | AI rejects a request that lacks sufficient context or conflicts with policy. | Human may override only with documented justification. |

---

## 5. AI Context Management

### 5.1 Context Sources (in order of priority)
1. **Architecture Standards** (e.g., Homelab Architecture Standard) – authoritative design constraints.
2. **Documentation Standard** – required documentation structure and content.
3. **Audit Standard Implementation Plan** – compliance expectations.
4. **Memory (ADRs, prior decisions)** – historical rationale.
5. **Repository State** – current code, configs, and CI status.
6. **Service Documentation** – per‑service operational guides.
7. **Current Project State** – open issues, backlog items.

### 5.2 Freshness & Expiration
- Context older than **30 days** **MAY** be considered stale and must be refreshed before use.
- Critical security context **MUST** be up‑to‑date at all times.

### 5.3 Conflict Resolution
- When two sources disagree, the source with the highest priority (see 5.1) **SHALL** prevail.
- AI **MUST** surface the conflict to the Human Operator for confirmation.

### 5.4 Validation
- Prior to each stage, the Orchestrator AI **SHALL** validate that required context is present and current; missing context **MUST** trigger an escalation.

---

## 6. AI Collaboration

- **Planner → Builder** – Planner hands off a verified implementation plan; Builder acknowledges receipt.
- **Builder → Reviewer** – Builder submits code; Reviewer performs self‑review and returns comments.
- **Reviewer → Auditor** – Reviewer hands off the reviewed artifact; Auditor validates compliance.
- **Auditor → Human** – Auditor presents an audit report; Human provides final approval or required remediation.
- All hand‑offs **SHALL** include explicit ownership metadata and timestamps.
- Duplicate effort **MUST** be avoided by requiring the Memory AI to surface existing related work before any new generation.
- Conflict between agents **MUST** be resolved by the Orchestrator AI invoking the Human Operator.

---

## 7. AI Risk Classification

| Risk Level | Typical Examples | Required Approvals | Audit Requirement | Rollback Requirement |
|------------|------------------|--------------------|--------------------|-----------------------|
| **Low** | Minor refactors, documentation updates. | None (auto‑approved) | Optional audit after merge. | No immediate rollback needed. |
| **Medium** | New service integration, non‑critical security config changes. | Human approval of architecture. | Audit **SHOULD** be performed within 24 h. | Rollback **MAY** be scheduled. |
| **High** | Production deployment, credential rotation, firewall rule changes. | Human **MUST** approve; may require multiple signatories. | Formal audit **MUST** be completed before merge. | Immediate rollback **MUST** be possible. |
| **Critical** | Data deletion, infrastructure‑wide changes, breaking API contracts. | Multi‑level Human approval **MUST** be recorded. | Comprehensive audit **MUST** be completed and signed off. | Immediate, automated rollback **MUST** be executed on failure. |

---

## 8. AI Escalation Matrix

| Escalation Trigger | Owner | Priority | Human Required | Can AI Continue? |
|--------------------|-------|----------|----------------|-------------------|
| Architecture conflict | Orchestrator AI | High | **Yes** (Architecture Owner) | No |
| Documentation conflict | Reviewer AI | Medium | **Yes** (Documentation Owner) | No |
| Security concern | Builder AI | Critical | **Yes** (Security Owner) | No |
| Lifecycle violation | Orchestrator AI | High | **Yes** (Service Lifecycle Owner) | No |
| Audit failure | Auditor AI | High | **Yes** (Audit Owner) | No |
| Breaking change without deprecation | Planner AI | Medium | **Yes** (Product Owner) | No |
| Data loss risk | Builder AI | Critical | **Yes** (Data Owner) | No |
| Infrastructure impact (e.g., storage re‑allocation) | Orchestrator AI | High | **Yes** (Infrastructure Owner) | No |
| Missing standard reference | Memory AI | Low | **Yes** (Standards Owner) | Yes (but must add reference) |
| Unknown behaviour / ambiguous request | Planner AI | Medium | **Yes** (Human Operator) | No |

---

## 9. AI Quality Gates

| Gate | Purpose | Validation Method | Responsible Role | Automatable? |
|------|---------|-------------------|-------------------|--------------|
| Planning Complete | Ensure a coherent, scoped plan exists. | Verify plan file against a template. | Planner AI | Yes |
| Architecture Approved | Confirm compliance with Homelab Architecture Standard. | Cross‑check against Architecture Standard sections. | Human + Auditor AI | Partially (human sign‑off required) |
| Documentation Complete | All affected artifacts have up‑to‑date docs. | Documentation lint + checklist. | Reviewer AI | Yes |
| Compose Validated | Verify Docker Compose files meet Docker Standard. | `docker compose config` validation. | Builder AI | Yes |
| Audit Passed | No high‑severity findings. | Audit report review. | Auditor AI | Yes |
| Tests Passed | Unit/integration tests succeed. | CI pipeline results. | Builder AI | Yes |
| Rollback Verified | Confirm rollback procedure works. | Simulated rollback test. | Orchestrator AI | Yes |
| Human Approval Recorded | Capture signed approvals for gated items. | Metadata audit. | Human Operator | No (requires signature) |

---

## 10. AI Prompt Governance

- **Versioning** – Every prompt template **MUST** carry a semantic version identifier.
- **Ownership** – Prompt owners are recorded in the prompt metadata.
- **Review** – Prompts **SHALL** undergo the same review process as code (Reviewer AI + Human).
- **Approval** – Critical prompts (those that affect security or production) **MUST** obtain Human approval.
- **Deprecation** – Deprecated prompts **MUST** be archived with a deprecation notice.
- **Testing** – Prompts **SHALL** be exercised against a curated test suite before release.
- **Documentation** – Prompt purpose, inputs, and expected outputs **MUST** be documented in the Prompt Registry (see Documentation Standard).
- **Changelog** – All changes to prompts **MUST** be logged with rationale.
- **Reuse** – Prompt reuse **SHALL** be encouraged; duplicate prompts **MUST** be consolidated.
- **Auditing** – Periodic audits of prompt usage **MUST** be performed (see Audit Standard).

---

## 11. AI Memory Governance

- **Persistent Memory** – Long‑term storage of ADRs, decisions, and policy documents **SHALL** be immutable and searchable.
- **Working Memory** – Session‑level context **MAY** be discarded after task completion unless explicitly retained.
- **Project Memory** – Context scoped to a single project **SHALL** be retained for the project’s lifecycle.
- **Temporary Context** – Short‑lived artefacts **MUST** expire after a defined TTL (default 24 h).
- **Retention** – Retention periods **SHALL** be defined per memory class and reviewed annually.
- **Validation** – Before use, memory entries **MUST** be validated against their source standard.
- **Conflict Resolution** – Conflicting memory entries **MUST** be presented to the Human Operator for resolution.

---

## 12. AI Continuous Learning

1. **Audit** → produces findings and lessons learned.
2. **Lessons Learned** → are captured in the Knowledge Base.
3. **Template Improvements** → update code and service templates.
4. **Documentation Updates** → refresh affected docs.
5. **Prompt Improvements** → refine prompt templates based on observed gaps.
6. **Future Projects** → benefit from the refined assets.

All steps **SHALL** be traceable to the originating audit.

---

## 13. AI Metrics (Governance‑Only)

| Metric | Description |
|--------|-------------|
| Planning Accuracy | Ratio of planned vs. actual outcomes (target ≥ 95 %). |
| Review Accuracy | Percentage of reviewer suggestions accepted without rework. |
| Audit Accuracy | Percentage of audit findings classified correctly. |
| Escalation Rate | Number of escalations per 100 tasks (target ≤ 5). |
| False‑Positive Rate | Ratio of escalations that were unnecessary (target ≤ 2 %). |
| Human Override Rate | Frequency of human overrides on AI decisions (target ≤ 3 %). |
| Documentation Coverage | Percentage of changed artefacts with up‑to‑date docs (target ≥ 98 %). |
| Prompt Reuse | Proportion of prompts reused across projects (target ≥ 70 %). |
| Automation Coverage | Share of quality‑gate validations performed automatically. |
| Knowledge Reuse | Frequency that prior ADRs or lessons are referenced in new work. |

---

## 14. AI Maturity Model

| Level | Name | Characteristics |
|-------|------|-------------------|
| 1 | **Ad Hoc** | AI used sporadically; no formal governance.
| 2 | **Assisted** | Basic guidelines exist; humans approve most outputs.
| 3 | **Standardized** | Full AI Development Standard applied; most gates automated.
| 4 | **Automated** | End‑to‑end pipelines with AI‑driven orchestration; human oversight limited to escalations.
| 5 | **Optimized** | Continuous learning loop closes; metrics drive iterative improvements.

---

## 15. AI Future Integration

The standard **MUST** remain agnostic to the underlying AI technology. It **SHALL** continue to apply when any of the following (or similar) agents replace current ones:
- Hermes
- Honcho
- MCP‑based agents
- OpenHands, Claude Code, Codex, etc.
Future agents may introduce new capabilities, but they **MUST** conform to the responsibilities, workflows, and gates defined herein.

---

## 16. Governance Review

- The AI Development Standard **SHALL** not duplicate governance content from the Architecture, Documentation, Service Lifecycle, or Audit Standards.
- All cross‑references use the **Document Title → Section Name** format and point only to existing standards within this repository.
- The standard is **implementation‑agnostic**, **vendor‑neutral**, and **future‑proof**.

---

## 17. Final Validation Checklist

- [ ] No duplicated governance content from existing standards.
- [ ] All references point to existing documents (Documentation Standard, Service Lifecycle Standard v1.0, Audit Standard Implementation Plan, Homelab Architecture Standard).
- [ ] Matrices and tables are internally consistent.
- [ ] Human approval boundaries are explicit and use RFC terminology.
- [ ] No reliance on specific AI products; only abstract roles are used.
- [ ] The **AI Tool Independence** section is present.
- [ ] The document follows the required naming and placement.

---

*Prepared for the Homelab Governance Roadmap – Phase 7.*
