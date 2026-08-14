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
- ✅ Canonical `Personal_Knowledge_Archive.md` created.
- ✅ `ChatGPT_History/` placeholder archive structure created.
- ⏳ Personal Knowledge material input (user-supplied) — pending.
- ⏳ Ingestion pipeline to Chroma / Honcho / Graphify — **later, separately
  approved**; not implemented now.

## Key documents

| Document | Purpose |
| --- | --- |
| `Personal_Knowledge_Archive.md` | Canonical curated archive (about me, preferences, technical environment, projects, decisions, history, relationships). |
| `ChatGPT_History/README.md` | Historical source archive structure (placeholders). |

## Constraints (preserved)

- Phase 15 (Council) remains **paused** and untouched.
- Phase 16 (MCP/Tools) remains complete.
- No new runtime, service, importer, memory/knowledge API, or Python created in
  this curation phase.
- Honcho / Chroma / Graphify architectures unchanged.
- Existing KORA / Council / Brainiac canonical content untouched.
