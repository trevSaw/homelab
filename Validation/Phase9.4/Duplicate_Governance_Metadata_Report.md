# Duplicate Governance Metadata Report

**Phase:** 9.4.1 (External Review Remediation / Final QA)  
**Branch:** `phase9.3`  
**Audit action:** Inventory only — **no files were deduplicated or modified** for this finding.

## Purpose

Some service documentation files contain more than one `## Governance Metadata` heading, inherited from earlier Phase 9 documentation duplication. Phase 9.4 appended `### Evidence References` under each occurrence so copies remain consistent. This report records the duplication as technical debt for a later documentation refactor.

## Detection Method

```bash
# Count ## Governance Metadata headings per service markdown
```

Files with count **> 1** are listed below.

## Affected Files

| File | `# Governance Metadata` count | `# Evidence References` count | Notes |
|------|-------------------------------|-------------------------------|-------|
| `Documentation/services/beszel/beszel.md` | 2 | 2 | Full documentation body appears duplicated; Evidence References present under both Governance Metadata sections. |
| `Documentation/services/jellyfin/jellyfin.md` | 2 | 2 | Same pattern as beszel. |
| `Documentation/services/traefik/traefik.md` | 2 | 2 | Same pattern as beszel. |

**Total affected files:** 3  
**Total duplicate Governance Metadata sections beyond the first:** 3 (one extra section each)

## Unaffected Services (single Governance Metadata)

`authentic`, `beszel_agent`, `calibre-web`, `code-server`, `CosmoOS`, `echoos`, `EchoOS`, `hermes`, `homepage`, `honcho`, `Hotio`, `n8n`, `NZBget`, `odysseus`, `ollama`, `portainer` — **16 / 19** services have exactly one `## Governance Metadata` section.

## Recommendation

**Normalize duplicated documentation sections during Phase 10 documentation refactoring.**

Suggested Phase 10 approach (recommendation only — not implemented here):

1. Keep a single canonical copy of Overview → Known Issues for each affected service.
2. Retain one `## Governance Metadata` block with one `### Evidence References` subsection.
3. Re-verify JSON ↔ markdown evidence consistency after deduplication.
4. Do not alter `service.json` evidence content as part of the markdown-only cleanup unless a separate schema phase requires it.

## Phase 9.4.1 Disposition

| Action | Status |
|--------|--------|
| List affected files | Done |
| Record duplicate counts | Done |
| Deduplicate content | **Deferred** (explicitly out of scope) |
| Modify affected files for this finding | **Not done** |
