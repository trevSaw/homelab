# Phase 17 — ChatGPT History → KORA Personal Knowledge Migration

**Status:** 🟡 **Started — curation phase** (2026-08-13)

## Purpose

Create a curated, canonical **Personal Knowledge Archive** from the user's
ChatGPT history and existing project knowledge — **not** a raw conversation
import.

```text
ChatGPT history
      ↓
historical analysis
      ↓
Personal Knowledge Archive      ← canonical, human-readable, machine-searchable
      ↓
KORA Knowledge / Chroma          ← searchable corpus (later)
      ↓
selective durable memory / Honcho ← selected durable personal memory (later)
```

Raw ChatGPT conversations remain **historical source material**
(`ChatGPT_History/`). The curated archive is the primary representation of what
KORA should know about the user and their history.

## Scope of this kickoff

- ✅ Roadmap updated (Phase 17 reframed).
- ✅ Canonical `Personal_Knowledge_Archive.md` created + populated (foundational
  user profile incorporated; authoritative KORA model `gpt-oss:20b-cloud`).
- ✅ `ChatGPT_History/` placeholder archive structure created.
- ✅ **Targeted Historical Enrichment Policy** documented (full ChatGPT history
  migration is **not** planned; historical enrichment is a policy, as-needed).
- ⏳ Ingestion pipeline to Chroma / Honcho / Graphify — **later, separately
  approved**; not implemented now.

## Phase 17 status

- Foundational user profile / archive / preferences / behavioral guidance /
  project context / architectural decisions — **Complete**
- Historical/superseded architecture — **Documented**
- Full ChatGPT history migration — **Not planned**
- Automatic historical memory migration — **Not planned**
- Targeted historical enrichment — **Optional / as-needed** (see policy)
- **KORA validation — Done (2026-08-14): PASS (7/8 core, 1 partial)**

### Remediation + validation summary

- **Cleaned Honcho test data:** removed the 8 Phase 14 harmless-test conclusions
  from peer `user` (Japanese curry ×2, ramen ×2, visit Japan next spring ×2,
  tea-over-coffee ×2). Legitimate conversational memories (wedding/groomsmen,
  children's art, operational notes) preserved.
- **Indexed the canonical archive** into jDocMunch (`local/homelab-docs`) —
  `Personal_Knowledge_Archive.md` is now retrievable via the same MCP path KORA
  uses (`mcp_jdocmunch_search_sections` / `get_section`).
- **KORA retrieval behavior:** added `PROFILE_RETRIEVAL_DIRECTIVE` to the KORA
  plugin (source hierarchy: canonical knowledge > project knowledge >
  Honcho-derived memory > model inference; current decisions override
  historical; surface conflicts).
- **Validation:** Who am I? ✅ · What is KORA? ✅ · Current architecture ⚠️
  (retrieves architecture decisions but not the explicit canonical path —
  lexical-search ranking) · Current model ✅ (gpt-oss:20b-cloud) · Previous
  model ✅ (Qwen 3 8B, superseded) · Import ChatGPT history? ✅ (no) ·
  Conflict handling ✅ · Major projects ✅ · Who am I? new session ✅.
- **Known limitation:** jDocMunch lexical (BM25) search ranks some sections
  inconsistently for vague queries; semantic search (embedding provider) would
  improve retrieval quality. Not changed in this remediation.

## Key documents

| Document | Purpose |
| --- | --- |
| `Personal_Knowledge_Archive.md` | Canonical curated archive (about me, preferences, technical environment, projects, decisions, history, relationships, behavioral instructions). |
| `Targeted_Historical_Enrichment_Policy.md` | KORA policy for historical enrichment — targeted/as-needed, never full-history migration. |
| `ChatGPT_History/README.md` | Historical source archive structure (placeholders). |

## Constraints (preserved)

- Phase 15 (Council) remains **paused** and untouched.
- Phase 16 (MCP/Tools) remains complete.
- No new runtime, service, importer, memory/knowledge API, or Python created in
  this curation phase.
- Honcho / Chroma / Graphify architectures unchanged.
- Existing KORA / Council / Brainiac canonical content untouched.
