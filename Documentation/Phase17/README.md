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
- KORA validation — **Next**

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
