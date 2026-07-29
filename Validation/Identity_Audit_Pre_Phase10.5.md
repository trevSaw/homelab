# Homelab Repository Identity Audit

**Scope:** Pre-Phase 10.5  
**Host identity:** mocha · Ubuntu Server · Docker Compose · Traefik · ZFS · single administrator  
**Date:** 2026-07-30  
**Runtime changes:** None (documentation, standards wording, comments, inventory trees, and removal of an unused employer compose file only)

---

## Summary

The repository is a personal homelab project. The audit found **explicit Mujin / employer leakage** (compose file + Proxmox apt-mirror runbook), plus softer corporate wording (“operations team”, “organisation”, “production platform”, “fleet”). Clear employer-specific content was removed or rewritten. Ambiguous governance / peer-review language was left for manual review so engineering quality is preserved.

**Mujin / `mujin.co.jp` / `mjpn-*` references are cleared from the live tree.**

---

## 1. Findings (work-related or identity risk)

| # | Reference | File | Why it appears work-specific | Recommended replacement | Fixed? |
|---|-----------|------|------------------------------|-------------------------|--------|
| 1 | Entire file `compose-mujin-production.yaml` (`ADMIN_EMAIL=…@mujin.co.jp`, `llm.mujin.co.jp`, `mujinpki`, Teams notify, Microsoft Entra vars) | `compose/ai/ollama-openwebui/compose-mujin-production.yaml` | Employer production Open WebUI stack, not mocha | Remove from personal repo (keep only mocha stacks: `compose.yaml`, `compose-nvidia.yaml`, `20b-olla-compose.yaml`) | **Yes — deleted** (unused; only listed in tree inventories) |
| 2 | Mujin Aptly mirror (`mjpn-tyo-apt01.mujin.co.jp`), GPG key, `MJPN_TYO_APT01`, corp IP `10.2.25.160`, terragrunt pfSense OOB rules | `Documentation/runbooks/ProxmoxTrixieUpgrade.md` | Work Proxmox upgrade against company apt mirror and corporate firewall | Official Debian + Proxmox no-subscription mirrors; personal firewall notes | **Yes — rewritten** |
| 3 | Tree / inventory listings of Mujin compose | `DirectoryTreeReport.md`, `DetailedDirectoryTree.md`, `homelab_file_list.txt` | Mirrored employer filename | Match remaining personal compose files | **Yes** |
| 4 | “approve wave schedule with **operations team**” | `Validation/Phase9.1/Phase9.1_Governance_Report.md`, `Phase9_Execution_Plan.md`, `Phase9.1_Combined_Validation.md` | Multi-team ops language | Homelab administrator | **Yes** |
| 5 | README “production‑grade governance hub”, “downstream consumption”, multi-repo CI/CD framing | `README.md` | Sounds like a corporate platform repo | Personal self-hosted hub; mocha; single administrator | **Yes** |
| 6 | “On-premise / **corporate** LLM gateways” | `services/odysseus/.env.example` | Corporate gateway assumption | Self-hosted / local LLM private CA | **Yes** |
| 7 | “across the **organisation**” / “**Organisations** may self‑assess” | `Architecture/standards/AuditStandardImplementationPlan.md` | Org-wide maturity language | Homelab / homelab administrator | **Yes** |
| 8 | Energy score notes “always-on **fleet**” | `scripts/audit/energy_audit.sh`, `Validation/Energy/Latest_Energy_Audit.md` | Fleet ops wording | “always-on container set” | **Yes** (script + Latest; dated Energy audits left as historical snapshots) |
| 9 | Roadmap “Production Approval”, “production environment/platform”, “Production Validation”, “Production deployments” | `Architecture/standards/StandardsRoadmap.md` | Enterprise go-live tone | Deploy readiness / homelab validation / personal platform | **Yes** (selective) |
| 10 | Audit README / Validation README “Homelab Governance repository” framing without personal host identity | `scripts/audit/README.md`, `Validation/README.md` | Could read as a corporate governance product | Personal Homelab repository | **Yes** |
| 11 | ServiceIndex “**Team** wiki” (Wiki.js) | `Services/ServiceIndex.md` | Team product framing | Personal wiki | **Yes** |
| 12 | Owner column `*Unassigned*` | `Validation/Phase9.1/Phase9_1_Report.md`, `Phase9.1_Combined_Validation.md` | Implies staffing / RACI vacancies | Homelab Administrator | **Yes** |
| 13 | “Supporting **Platform**” / “not critical for **production**” | Phase 9.1 priority tables | Platform/prod org tone | Supporting Service / core homelab infrastructure | **Yes** |
| 14 | “None (**internal**)” | `Architecture/standards/AI-Development-Standard.md` | Internal-corp connotation | None (homelab-local) | **Yes** |
| 15 | “speculative **business** importance” | Phase 9.1 governance reports | Business ranking language | Operational criticality | **Yes** |

---

## 2. Items requiring manual review

| # | Item | Location | Notes |
|---|------|----------|-------|
| M1 | `generate_kerberos_risk_assessment.py` (Azure AD Connect, SIEM, “organizations”, “Pilot 5–10% of users”) | `scripts/helpers/generate_kerberos_risk_assessment.py` | Enterprise identity / WHfB risk doc generator. Not mocha runtime. Keep as personal research, relocate to knowledge-base, or delete. |
| M2 | “Peer review” / Reviewer roles | `ADRStandard.md`, `DocumentationStandard.md`, `Service Lifecycle Standard v1.0.md`, `AuditStandardImplementationPlan.md`, ADR template | Valid for solo PR self-review; optionally reword to “self-review via pull request” if you want zero team implication. |
| M3 | Sections titled **Change Management** | `DockerStandard.md`, `DocumentationStandard.md` | Documenting how *you* change docs/compose — keep as engineering practice unless it grows CAB/board language. |
| M4 | “Homelab **Governance**”, QA **signoff**, Governance Freeze | Widespread under `Architecture/`, `Documentation/governance/`, `Validation/Phase9*` | Intentional personal standards framework from Phases 9–10. Not employer-specific. Decide whether to keep the governance vocabulary or soften further before Phase 10.5. |
| M5 | Service status **Production** (= running in the homelab) | `Services/ServiceIndex.md` and service docs | Defined locally as “Running in the homelab”. Recommend **keep**. |
| M6 | “**enterprise** HDDs / Exos drives” | `Documentation/runbooks/ZFSCleanupAndMonitoring.md` | Drive *class* (enterprise SATA), not employer. Recommend **keep**. |
| M7 | Dated Energy audits still say “always-on fleet” | `Validation/Energy/Energy_Audit_*.md` (historical) | Generated snapshots. Leave as history or regenerate after next energy audit run. |
| M8 | Paths `/home/trevor.sawyer/homelab-data/...` in older compose under `compose/ai/` | `compose/ai/ollama-openwebui/compose.yaml`, `compose/ai/llama/compose.yml` | Personal username paths — **not** Mujin. Confirm they match mocha layout (`/hive`, `/mnt/monarch`) vs legacy laptop paths; out of scope for identity-only unless you want path cleanup later. |
| M9 | Proxmox upgrade runbook still present | `Documentation/runbooks/ProxmoxTrixieUpgrade.md` | Rewritten for official mirrors. mocha is Ubuntu Server — confirm you still want a Proxmox guide in this repo or move it to knowledge-base. |
| M10 | GitHub Actions CI | `.github/workflows/*` | Markdown/metadata/index validation only. No corporate deploy/approval workflows found. **No change required.** |
| M11 | `services/*/compose` runtime files | `services/` | Inspected for Mujin/employer refs — none found. **Do not touch** for this audit. |

---

## 3. Explicitly preserved (not work-specific)

- Docker / Compose / shell / logging / healthcheck / resource-limit standards  
- Validation, CI lint, documentation quality  
- Homelab Governance phase history (personal initiative naming)  
- Hardware term “enterprise HDD”  
- Status label “Production” = deployed on mocha  

---

## 4. Success criteria check

| Criterion | Status |
|-----------|--------|
| Personal Homelab identity clear in root README | Met |
| Host mocha / Ubuntu / Compose / ZFS / Traefik / local AI / media / single admin | Stated; infrastructure unchanged |
| No Mujin / mujin.co.jp / mjpn-* in tree | Met (post-delete + runbook rewrite) |
| No employer compose / corporate apt mirrors | Met |
| Runtime Compose / networks / Traefik / ZFS / apps unchanged | Met |
| Ambiguous items listed for manual review | Met |

---

## 5. Recommended next steps before Phase 10.5

1. Decide fate of **M1** (Kerberos risk generator) and **M9** (Proxmox guide vs knowledge-base).  
2. Optionally soften **M2** peer-review language.  
3. Re-run energy audit so Latest + new dated report use “container set” wording.  
4. Confirm older `compose/ai/*/compose.yaml` bind paths vs mocha (`/hive`, `/mnt/monarch`) in a later path-alignment pass (not identity).  

---

*End of identity audit report.*
