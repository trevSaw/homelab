---
title: Documentation to Obsidian notes — governance
tags:
  - obsidian
  - governance
  - import
aliases:
  - Doc import standard
  - Transform docs for Obsidian
---

# Documentation → Obsidian notes (governance)

Standard for turning existing markdown (or plain notes) into vault notes that work with **Inbox → tag → Auto Note Mover**. Use this with [[obsidian-local-vault-automation]] (plugins, folders, `tags.md`).

Audience: a **home AI** (or human) importing docs into a local Obsidian vault. Prefer **copies**; leave originals where they live unless told otherwise.

---

## Principles

1. **One note, one purpose.** Do not dump a whole repo README tree into one file.
2. **Routing tags first.** Every imported note gets exactly one: `weekly-sync`, `writeup`, or `guide` (plus topic tags from `Settings/tags.md`).
3. **Filename = identity.** Prefer `kebab-case.md` or `YYYY-MM-DD.md` for standups. No `Untitled`.
4. **Obsidian-native.** Use `[[wikilinks]]`, YAML frontmatter, and folder MOCs — not bare relative HTML links as the primary graph.
5. **Light cleanup only.** Fix spelling that blocks understanding; do not rewrite meaning or invent status.
6. **Controlled vocabulary.** Only tags in `Settings/tags.md`. If a new topic appears, **add it to `tags.md` and a mover rule** before using it.
7. **Do not auto-tag Templates or MOCs.** Never run batch AI Tagger on `Templates/`, `Home.md`, or folder indexes.

---

## What to import vs skip

| Import | Skip |
|--------|------|
| Your writeups, guides, runbooks, postmortems | Vendor / provider README inside `.terraform` |
| Meeting / weekly sync dumps | Git repo READMEs unless they are *your* ops docs |
| Project roadmaps and troubleshooting notes | Backup copies (`*-backup-*`), `temp/` duplicates |
| Templates you own (postmortem template) | Secrets, credentials, private keys |

Homelab vs work: keep separate vaults or clearly separate top-level folders. Do not mix work postmortems into a personal-only vault without an explicit ask.

---

## Classify before you write

| Source looks like… | Type | Destination (after tag) | Required tags |
|--------------------|------|-------------------------|---------------|
| Dated standup / sync bullets | weekly-sync | `Weekly Sync/` | `weekly-sync` + topics |
| Incident / postmortem / cert renewal | writeup | `Writeups/<topic>/` | `writeup` + e.g. `postmortem`, `tls` |
| How-to / roadmap / host setup | guide | `Guides/<topic>/` | `guide` + e.g. `guide-powerdns` |
| Index of many notes | moc | vault root or folder root | `moc` + `AutoNoteMover: disable` |

Topic folders follow the vault layout in the automation playbook (DNS, Aptly, Azure, TLS, etc.). If nothing fits, create a subfolder **and** add tag + mover rule in the same change.

---

## Note shape (every imported file)

```yaml
---
date: YYYY-MM-DD          # optional; use for events / standups
tags:
  - writeup               # exactly one of: weekly-sync | writeup | guide
  - powerdns              # topic tags from tags.md only
aliases: []               # optional short names
AutoNoteMover: disable    # only on MOCs / indexes / templates
---

# Clear title

Body…
```

- Title heading should match the note’s purpose (not the old path).
- Prefer `[[wikilinks]]` to related notes (`[[PowerDNS]]`, `[[Weekly Sync]]`).
- Keep lists and headings; strip ASCII banners / decorative art.
- Do not put `#` on lines in `tags.md` (the tagger treats `#` lines as comments).

---

## Transform pipelines

### A. Multi-date dump (one file, many weeks)

Example: a single `weekly_sync_up` file with `2026-AUG-11` sections.

1. Split **one note per date**.
2. Filename: `YYYY-MM-DD.md` (normalize `2026-AUG-11` → `2026-08-11`).
3. Frontmatter: `date`, `tags: [weekly-sync, …topics…]`.
4. Light grammar cleanup; keep bullets.
5. Add an index MOC (`Weekly Sync.md`) with wikilinks to each date.
6. Optional stub notes for recurring threads (project names) with `AutoNoteMover: disable` if they live under an excluded folder, or rely on folder excludes.

### B. Folder of existing `.md` writeups

1. **Copy** into the vault (do not move originals unless asked).
2. Group into `Writeups/<area>/` or `Guides/<area>/` by content, not by old path alone.
3. Add frontmatter + routing tag if missing.
4. Create or update a folder MOC (`Writeups.md`, `Guides.md`) with wikilinks.
5. Extend `Settings/tags.md` and Auto Note Mover rules for any new area.
6. Link stubs / MOCs from `Home.md`.

### C. Single long guide

1. One note (or split only if it is clearly two documents).
2. Tag as `guide` + specific guide tag.
3. Filename: descriptive `kebab-case.md`.
4. Drop into Inbox **or** place directly in the target folder if the vault excludes are already set and you are doing a bulk import offline.

### D. Bulk import (AI or script)

1. Land copies in **Inbox** (or a staging folder that is **not** excluded).
2. Ensure frontmatter + routing tags match `tags.md`.
3. Let Auto Note Mover file them — or move manually once, then rely on excludes so filed notes are never reshuffled.
4. Update MOCs last.
5. Do **not** run “tag all vault” until excludes cover `Weekly Sync`, `Writeups`, `Guides`, `Templates`.

---

## Vocabulary governance

`Settings/tags.md` is the source of truth (one tag per line, no `#`).

When introducing a topic:

1. Add the tag line to `tags.md`.
2. Add an Auto Note Mover rule (folder + `#tag`), **below** weekly-sync / guide-specific rules as appropriate.
3. Prefer specific guide tags (`guide-powerdns`) over a bare `guide` that fights topic rules.
4. Use Tag Wrangler to merge invented Hybrid tags into the controlled set.

Routing tags (`weekly-sync`, `writeup`, `guide`) are for **filing**. Topic tags are for **search and graph**.

---

## Quality bar (done means)

- [ ] Note has YAML `tags` with one routing tag from the allowed list  
- [ ] Filename is stable (`kebab-case` or `YYYY-MM-DD`)  
- [ ] Linked from the right MOC (`Home`, `Writeups`, `Guides`, or `Weekly Sync`)  
- [ ] No secrets copied from source trees  
- [ ] Originals untouched (unless user asked to move)  
- [ ] New tags/rules added if a new folder was created  

---

## Prompt for a home AI (paste)

```text
You are importing my documentation into an Obsidian vault that uses Inbox → tags → Auto Note Mover.

Follow the governance note: "Documentation → Obsidian notes (governance)" and the automation playbook "Obsidian local vault automation".

Rules:
- Copy files; do not delete originals unless I say so.
- One note per weekly date; normalize dates to YYYY-MM-DD.
- Every note needs frontmatter with exactly one routing tag: weekly-sync, writeup, or guide.
- Only use tags listed in Settings/tags.md. If you need a new tag, add it to tags.md and describe the Auto Note Mover rule.
- Add wikilinks and update MOCs (Home, Writeups, Guides, Weekly Sync).
- Light cleanup only; keep my meaning.
- Never AI-tag or mover-file Templates/ or MOC notes; put AutoNoteMover: disable on indexes.
- Skip vendor READMEs, backups, and secrets.

When finished, list: files created, folders used, tags added, and anything you skipped.
```

---

## Relation to automation playbook

| Doc | Job |
|-----|-----|
| [[obsidian-local-vault-automation]] | Plugins, folders, Templater, mover rules, Ollama models |
| This note | How to turn existing docs into notes that obey that system |

Give both to the home AI. Setup first, then import.
