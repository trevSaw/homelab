---
title: Obsidian local vault automation
tags:
  - obsidian
  - ollama
  - homelab
---

# Obsidian local vault automation

Playbook from a work-vault setup (Inbox → tag → file) for reuse on a **home** Obsidian instance with **local Ollama**. Copy this note into the home vault and adjust folder names if you want.

For turning existing docs into vault notes, see the companion standard: [Documentation → Obsidian notes (governance)](obsidian-doc-to-notes-governance.md). Give **both** files to a home AI.

Hardware this was tuned for: Intel Core Ultra 7 155U (iGPU, IPEX-LLM Ollama), ~32 GB RAM. If home is similar, keep small models.

---

## What you get

1. New notes land in **Inbox**.
2. Weekly notes are created from a **Templater** template, named `YYYY-MM-DD`, tagged `#weekly-sync`.
3. **Auto Note Mover** files them into the right folder from tags or the date in the title.
4. **AI Tagger Universe** (Ollama) picks tags from a controlled list (`tags.md`). You run it **once per note**, not on every keystroke.

Tagging is **not** fully hands-off. Filing after tags exist **is** automatic if Auto Note Mover is set to Automatic.

---

## Vault layout

```text
vault/
├── Home.md                 # index / MOC
├── Inbox/                  # landing zone only
├── Templates/              # Templater templates (exclude from mover)
├── Settings/
│   └── tags.md             # allowed tags for AI Tagger (one per line, no #)
├── Weekly Sync/            # dated meeting notes
├── Writeups/               # topic subfolders
└── Guides/                 # topic subfolders
```

**Default new-note folder:** `Inbox`  
Settings → Files and links → Default location for new notes → In the folder specified → `Inbox`.

**Do not exclude Inbox** in Auto Note Mover. Notes must be *in* Inbox so they can *leave* Inbox.

Exclude from Auto Note Mover (and from AI Tagger batch runs):

- `Weekly Sync`
- `Writeups`
- `Guides`
- `Templates`

On MOC notes (`Home.md`, folder indexes), add frontmatter:

```yaml
AutoNoteMover: disable
```

---

## Plugins

### Core

- Templates (folder = `Templates`, date format `YYYY-MM-DD`)
- Tag pane, Properties, Command palette
- Bases (optional). New Bases also go to Inbox and are named `Untitled.base` — rename or delete miss-clicks.

### Community (this stack)

| Plugin | Role |
|--------|------|
| **Templater** | Create dated weekly notes in one command |
| **Auto Note Mover** | File notes by tag / title regex |
| **AI Tagger Universe** | Tags via local Ollama |
| **Tag Wrangler** | Merge/rename junk AI tags |
| **Homepage** | Open `Home.md` on launch (not a random folder) |

Optional later (one chat plugin, not a second tagger):

| Plugin | Role |
|--------|------|
| **Copilot** (Logan Yang) | Summarize / continue writing via Ollama |
| **Smart Connections** | Related notes via embeddings |

Do **not** run Copilot + Local GPT + Text Generator together on one small Ollama.

---

## Weekly notes (Templater)

Template folder: `Templates`.

File: `Templates/Weekly Sync.md`

```text
<%*
await tp.file.rename(tp.date.now("YYYY-MM-DD"))
-%>
---
date: <% tp.date.now("YYYY-MM-DD") %>
tags:
  - weekly-sync
---

# Weekly Sync — <% tp.date.now("YYYY-MM-DD") %>

- 
```

**Create a weekly note:** Command palette → **Templater: Create new note from template** → **Weekly Sync**.

Do **not** use `Ctrl+N` + core **Insert template**. Core Templates will not run `<% %>` and will not rename the file. An `Untitled.md` with `#weekly-sync` can get filed as `Untitled`.

Flow:

1. Templater creates the note in **Inbox**, renames it to today `YYYY-MM-DD`, adds `#weekly-sync`.
2. Auto Note Mover (Automatic) moves it to **Weekly Sync**.

Never run AI Tagger on files inside `Templates/` — the template itself can get extra tags and get moved (this happened once: template landed in `Guides/Azure`).

---

## Auto Note Mover

- Trigger: **Automatic**
- Regex for tags: **off**
- Tags **must** start with `#`
- Rules run **top to bottom**; **first match wins**

Suggested rule order:

| Destination | Match |
|-------------|--------|
| `Weekly Sync` | Title regex `^\d{4}-\d{2}-\d{2}` |
| `Weekly Sync` | `#weekly-sync` |
| `Guides/PowerDNS` | `#guide-powerdns` |
| `Guides/Azure` | `#azure-workbooks` |
| `Guides/Azure` | `#guide-azure` |
| `Guides/Windows` | `#windows-migration` |
| `Writeups/TLS & Certificates` | `#postmortem` |
| `Writeups/TLS & Certificates` | `#tls` |
| `Writeups/Aptly` | `#aptly` |
| `Writeups/Azure & Windows` | `#azure-update-manager` |
| `Writeups/Azure & Windows` | `#azure` |
| `Writeups/Atlassian` | `#jira` |
| `Writeups/Atlassian` | `#confluence` |
| `Writeups/Proxmox` | `#proxmox` |
| `Writeups/DNS` | `#powerdns` |

**Guide rules must sit above topic writeup rules.** A note tagged `#guide` and `#powerdns` will otherwise match `#powerdns` and go to `Writeups/DNS`. Prefer specific tags (`#guide-powerdns`), not a generic `#guide`.

The UI **clips** long folder/tag names. Click into the field and confirm the full string (`#azure-update-manager`, `Writeups/Azure & Windows`).

---

## AI Tagger Universe + Ollama

Endpoint: `http://localhost:11434/v1/chat/completions`

| Setting | Value |
|---------|--------|
| Service | Local LLM |
| Mode | **Hybrid** or **Predefined only** (stricter) |
| Tag source | **From predefined tags file** |
| File | `Settings/tags.md` |
| Preserve existing tags | **On** (`replaceTags: false`) |
| Nested tags | Off |
| Format | kebab-case |
| Max generated tags | 3 |
| Temperature | `0` if you want less invention |

Custom prompt:

```text
Choose tags only from this vault's existing tags when possible.
Always include exactly one routing tag: weekly-sync, writeup, or guide.
If it is a guide, also add the specific tag when it fits: guide-powerdns, guide-azure, azure-workbooks, windows-migration.
Topic tags allowed: powerdns, aptly, azure, azure-update-manager, tls, postmortem, proxmox, jira, confluence, whfb, tickets, hardware.
Use kebab-case. Do not invent new tags. Do not remove existing tags.
```

Exclude folders in **AI Tagger → Manage**: `Weekly Sync`, `Writeups`, `Guides` (and `Templates`). Do not run “tag entire vault” until those excludes are saved.

The plugin’s exclude description mentions Search/Graph; for this plugin it still means **do not auto-tag these folders**.

### `Settings/tags.md`

One tag per line, **no `#`**. Lines starting with `#` are **ignored** (treated as comments/headings).

```text
weekly-sync
writeup
guide
guide-powerdns
guide-azure
azure-workbooks
windows-migration
postmortem
tls
aptly
azure
azure-update-manager
jira
confluence
proxmox
powerdns
whfb
tickets
hardware
```

**Hybrid + file:** model picks from this list **and** may invent extras.  
**Predefined only + file:** only this list (best match for mover rules).  
**Source = vault:** ignores `tags.md`; uses every tag already in the vault.

This file is **not** an Obsidian template and does **not** go in `Templates/`. Tag Templates in the plugin UI is a different feature.

---

## Writeups / other notes

1. `Ctrl+N` or new note in **Inbox**.
2. Write.
3. Command: **AI Tagger** on **that note only**.
4. Auto Note Mover files it from the routing/topic tags.

Weekly notes often do not need AI Tagger; the template already has `#weekly-sync` and a dated title.

---

## Models (local Ollama)

Tagging is classification, not coding. Prefer a small **instruct** model.

| Model | Role on a 155U-class iGPU |
|-------|---------------------------|
| `llama3.2:3b-instruct-q4_K_M` | Safe, fast default (~2 GB) |
| `gemma4:e2b` | Try next — usually better instruction-following, similar cost |
| `gemma4:e4b` | Better quality, ~5–6 GB Q4; use for Copilot chat if E2B is already snappy |
| `qwen2.5-coder` / `llama3.1:8b` | Too big / wrong specialty for tags |

```bash
ollama pull gemma4:e2b
```

Point AI Tagger at `gemma4:e2b` and **Test Connection**. If it is as fast as Llama 3.2 3B, keep it for tags. If the box swaps or stalls, revert.

Gemma 4 needs a **recent** Ollama. An older `ipex-llm` container may fail or crawl; that is an image limit, not a reason to jump to 8B.

Do **not** tag-on-every-keystroke on this hardware.

---

## Optional AI next

- **Copilot:** same `localhost:11434`, E2B for speed or E4B for nicer prose. Summarize / rewrite current note.
- **Smart Connections:** small **embed** model for “related notes,” not the chat model.

Keep **AI Tagger** as the only tagger so Auto Note Mover’s tag list stays stable. Use Tag Wrangler when Hybrid invents `#dns-docker` — merge into `#powerdns`.

---

## Pitfalls

| Symptom | Cause |
|---------|--------|
| `Untitled.md` in Weekly Sync | Created with `Ctrl+N` / core template; rename never ran |
| `Untitled.base` in Inbox | Accidental new **Base**; default folder is Inbox |
| Template vanished from `Templates/` | AI Tagger tagged the template; mover filed it |
| Guide went to Writeups | `#powerdns` rule above `#guide-powerdns` |
| Homepage opens junk | Homepage set to “Random in folder” / wrong name — point it at `Home.md` |
| Tags do not match mover | `tags.md` used `#tag` (stripped) or mode is Generate without the file |

---

## Home-instance checklist

1. Create folders: Inbox, Templates, Settings, plus whatever you file into.
2. Install Templater, Auto Note Mover, AI Tagger Universe, Tag Wrangler, Homepage.
3. New notes → Inbox. Template folder → Templates.
4. Paste the weekly Templater file. Exclude `Templates` from the mover.
5. Add mover rules (date + tags). Exclude already-filed folders.
6. Add `Settings/tags.md`. AI Tagger: hybrid or predefined, source = file, preserve tags on.
7. Ollama up on `11434`. Model: `llama3.2:3b` or `gemma4:e2b`.
8. Smoke test: Templater → Weekly Sync → note appears under Weekly Sync as `YYYY-MM-DD.md`.
9. Smoke test: Inbox note about a topic → AI Tagger → mover files it.

Homepage: open **`Home.md`** on startup, not a random Inbox file.
