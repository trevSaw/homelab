# KORA External Web Research Validation — Phase 5

**Date:** 2026-10-06
**Scope:** Integrate the internal SearXNG service into KORA/Hermes as the
external web-research mechanism, and validate with a real research task.
**ADRs:** ADR-0014 (SearXNG service), ADR-0015 (KORA web research)
**Result:** **PASS** — KORA discovered and researched a real upstream repository
via SearXNG + OpenCode Go delegation, with no deployment and no boundary change.

## 1. Audit (before changes)

| Item | Finding |
| --- | --- |
| Hermes web capability | Native `web` toolset (`web_search`, `web_extract`) with a bundled SearXNG provider plugin (`plugins/web/searxng`). |
| Selection keys | `web.search_backend` / `SEARXNG_URL`; autodetect uses `SEARXNG_URL`. |
| `platform_toolsets` | `api_server` and `discord` = `[connections, file, kora, taskbridge, terminal, delegation]` — **no `web`**. |
| Extract providers | Only third-party (keyless exa/parallel/firecrawl/keenable or keyed); SearXNG is **search-only**. |
| MCP servers | jdocmunch, context7, graphify, taskbridge (unchanged). |
| KORA `pre_tool_call` | Allow-by-default + destructive-name guard; records every tool call. |
| Defect found | The guard matched the substring `"rmi"` inside **`terminal`** → all shell use (including delegated children) was silently blocked. |

## 2. Changes

| Change | Where |
| --- | --- |
| `SEARXNG_URL=http://searxng:8080` | `services/hermes/compose.yaml` (+ `.env.example`); non-secret |
| `web.search_backend: searxng`, `web.keyless_fallback: false` | Hermes `config.yaml` (appdata; backed up `config.yaml.bak-phase5-*`) |
| `web` enabled for `api_server` + `discord` | `platform_toolsets` in `config.yaml` |
| `RESEARCH_DIRECTIVE` (source-selection policy) | `services/hermes/plugin/kora/__init__.py` `pre_llm_call` |
| Destructive guard → whole-token match | `services/hermes/plugin/kora/__init__.py` `pre_tool_call` |
| SearXNG engine tuning (`github` enabled + categorised; dead engines disabled) | `services/searxng/config/settings.yml` |

Hermes was recreated (operator/control-plane) and the KORA plugin redeployed to
`/opt/data/plugins/kora/` (backup `__init__.py.bak-phase5-*`).

## 3. Integration verification

| Check | Result |
| --- | --- |
| `SEARXNG_URL` in container env | `http://searxng:8080` |
| Active search provider (resolved) | `searxng` |
| Active extract provider | `None` (keyless disabled — no third-party egress) |
| `web` toolset — `api_server` | enabled |
| `web` toolset — `discord` | enabled |
| `web_search` live call | returned `Casvt/Kapowarr` (GitHub engine) |
| `RESEARCH_DIRECTIVE` in KORA context | present |
| Hermes health | healthy |

## 4. End-to-end validation (api_server / Open WebUI path)

**Task:** *"Research https://github.com/Casvt/Kapowarr and prepare a governed
deployment plan. Do not deploy."* (delivered over `POST /v1/chat/completions`,
model `KORA`, fresh session).

**Trace (from `agent.log` / `kora-explain/records.jsonl`):**

1. KORA called `web_search` → SearXNG (searxng provider) → 9 results.
2. KORA called `delegate_task` (first attempt malformed: "missing a goal"; retried).
3. The **OpenCode Go child** (`model=deepseek-v4-flash provider=opencode-go`,
   session `20261006_190445_d50be7`) ran `terminal` (`git clone … Kapowarr`) and
   `read_file` on the repository.
4. KORA synthesized a governed plan and cited the upstream source.

**Evidence — artifact on disk:**

```
/opt/data/cache/scratch/Kapowarr/docker-compose.yml   (cloned from upstream)
```

**Evidence — KORA's parsed facts vs. real upstream (`Casvt/Kapowarr/docker-compose.yml`):**

| Fact | Upstream | KORA | Match |
| --- | --- | --- | --- |
| Image | `mrcas/kapowarr:latest` | `mrcas/kapowarr:latest` | ✓ |
| Ports | `5656:5656` | `5656:5656` | ✓ |
| Volumes | `kapowarr-db:/app/db`, `/path/to/download_folder:/app/temp_downloads`, `/path/to/comics:/comics` | same | ✓ |
| Env | `PUID=0`, `PGID=0`, `TZ=Etc/UTC` | same | ✓ |

**Conclusion:** KORA genuinely discovered and researched the upstream repository
without the user pasting the Compose file. `web_extract` was unavailable (by
design); the fetch was performed by the OpenCode Go child's `terminal`, exactly
as the policy directs.

## 5. Findings / remediation

- **F1 — Terminal false-positive (fixed).** KORA's destructive-name guard matched
  the substring `"rmi"` in `terminal`, blocking all shell use. Replaced with a
  whole-token match: `terminal` allowed; `*.remove` / `*.prune` / `*.exec` /
  `*.wipe` remain blocked. No new privilege beyond the already-configured
  `terminal` toolset; KORA still authorizes/records every call.
- **F2 — Environment blocks general search (mitigated).** The host egress IP is
  blocked/CAPTCHA'd by general engines (Mojeek `403`; Bing returns anti-bot junk;
  the existing Odysseus SearXNG fails identically). Enabled SearXNG's `github`
  engine (official GitHub API, works from here) as the reliable software
  discovery path and disabled dead engines.
- **F3 — `web_extract` unavailable (by design).** SearXNG is search-only and the
  alternatives are third-party; `web.keyless_fallback: false` prevents silent
  third-party egress. Pages/repos are fetched via `terminal`/delegation.
- **F4 — Delegation call quality.** The local model's first `delegate_task` was
  malformed ("missing a goal") and it retried successfully.
- **F5 — Model fabrication (limitation, not integration).** In the plan, KORA
  suggested pinning `mrcas/kapowarr:1.3.5`; upstream tags stop at `v1.3.2`
  (GitHub + Docker Hub). The `RESEARCH_DIRECTIVE` forbids invented versions —
  this is a local-model reliability issue to monitor.
- **F6 — Hermes approval gates destructive commands.** A delegated
  `rm -rf … && git clone` was returned as `pending_approval`; the child then
  cloned without the destructive prefix. Behaviour is correct.

## 6. Security boundary confirmation

No Docker socket in Hermes; no new runtime; no Task Bridge; KORA retained as the
governance layer (all tool calls recorded). SearXNG is internal-only (no
published ports). `web_extract` third-party egress disabled. No production
deployment was performed.

## 7. Follow-ups (not done)

- Optional: enable an approved `web_extract` backend if third-party egress is
  ever sanctioned (would improve one-call page fetching).
- Model reliability: consider constraining/validating version claims in KORA's
  plan output.
- Optional: consolidate the Odysseus-local SearXNG onto the shared instance.

---

# Phase 5.1 — Research Evidence/Provenance Remediation

**Date:** 2026-10-06
**Scope:** The first real Kapowarr research/plan task promoted model inference
(invented image tag `mrcas/kapowarr:v2.18.1-20241005`, fabricated homelab paths,
`kapowarr.example.com`, `/health`) into factual deployment claims even though the
repo and the delegated OpenCode child returned accurate evidence.
**Result:** **PASS** (read-only regression) — all initial failures resolved.

## 8. True root cause (deeper than the audit first reported)

The audit's "evidence/provenance gap" was real but **not the operative cause**.
The operative cause was found by inspecting the effective prompt:

- Hermes caps hook-injected context via `tools/hook_output_spill.py`
  (`hooks.output_spill.max_chars`, default **10000**). Above the cap it replaces
  the payload with a **500-char head + 500-char tail** preview plus a spill path.
- KORA's `pre_llm_call` context (all directives) totals **~18.2 KB**, so it was
  always spilled — only ~1 KB reached the model. The body of `RESEARCH_DIRECTIVE`
  (and of `LIVE_STATE`, `QBIT`, `DOCKER_ADMIN`, …) **never reached the model**;
  the evidence contract rules were silently dropped.
- Evidence: `messages.api_content` showed
  `[plugin hook output truncated — 18,513 chars …]`; the model only received
  `--- head ---` (start of the context) and `--- tail ---` (end of
  `RESEARCH_DIRECTIVE`).

So the model invented versions/paths because the very rules forbidding it were
not in its context. Directive prose alone could not fix a delivery problem.

## 9. Remediation

| Change | Where |
| --- | --- |
| New `RESEARCH_EVIDENCE_CONTRACT` (990 chars) — four-section output contract, evidence taxonomy, no-invented-values, conflict-stop, no-unread-citations, placeholder ban, discovery-failure semantics, delegation-integrity | `services/hermes/plugin/kora/__init__.py` |
| `RESEARCH_EVIDENCE_CONTRACT` **bookended** (first AND last) in `pre_llm_call` so head[0:500] ∪ tail[-500:] always covers it | `services/hermes/plugin/kora/__init__.py` |
| New `RESEARCH_EVIDENCE_PROTOCOL` (long form) retained for configs where the full context fits | `services/hermes/plugin/kora/__init__.py` |
| Deterministic guard `_evidence_check` in `transform_llm_output` — flags placeholder tokens (`example.com`, `/path/to/`, `<hostname>`, TBD) and Compose-bearing plans missing the four evidence headings; appends a visible "DO NOT TREAT AS DEPLOYABLE" note; never blocks conversation, no new runtime/privilege | `services/hermes/plugin/kora/__init__.py` |
| `plugin.yaml` version `0.3.0 → 0.4.0` | `services/hermes/plugin/kora/plugin.yaml` |

No Compose/DNS/Traefik/SearXNG/service-config change; no new MCP/bridge/runtime;
no new privilege. Plugin redeployed to `/opt/data/plugins/kora/` (backups
`__init__.py.bak-phase5.1-*`).

## 10. Validation (read-only; model = gpt-oss:20b-cloud unless delegated)

| Test | Result |
| --- | --- |
| Guard unit checks (conversation / placeholder / plan-missing-sections / plan-with-sections) | PASS — conversation silent; violations flagged |
| **T1 Kapowarr** | PASS — four sections; real `V1.3.2` + `mrcas/kapowarr:latest`; no `v2.18.1`/`1.3.5`/`example.com`/`/hive/series/comics`/`/hive/downloads/*`; `/health` flagged unverified; downloader integration under UNRESOLVED |
| **T2 generic service (Uptime Kuma)** | PASS — four sections; real `louislam/uptime-kuma:2`; no invented tag/hostname; unknowns under UNRESOLVED |
| **T3 normal conversation** | PASS — no forced four-section format; no guard noise |
| **T4 delegation integrity** | PASS — child's `mrcas/kapowarr:latest` returned verbatim, not substituted |
| **T5 failed discovery (fictional project)** | PASS — UPSTREAM/HOMELAB FACTS empty; all values under UNRESOLVED; no fabricated registry/tag/ports |

## 11. Security / governance regression

No Docker socket in Hermes; `pre_tool_call` still blocks destructive names and
requires `confirm=true` for writes; SearXNG internal-only (no published ports);
no new MCP; no Task Bridge; no new egress; Discord/Open WebUI paths unchanged.

## 12. Remaining limitations

- **Context truncation — RESOLVED (Phase 5.1b):** the directive set was
  compacted from ~18.2 KB to **9,750 chars** (< the 10,000 spill cap), so the
  **full** payload (`LIVE_STATE`, `QBIT`, `DOCKER_ADMIN`, `DELEGATION`,
  `RESEARCH` included) now reaches the model with **no spill**. The contract
  remains bookended as a safeguard, and is injected only for
  research/plan/deployment intent so normal conversation is unaffected. The
  global spill cap was **not** changed.
- The guard is conservative and can false-positive on legitimately quoted
  upstream placeholders (e.g. the upstream compose's `/path/to/...`).
- `HOMELAB FACTS` can still contain convention-derived assumptions presented as
  facts (e.g. a suggested `/hive/comics`); the contract reduces but does not
  eliminate this in a small model.
- Model output remains non-deterministic; the guard is defense-in-depth, not a
  proof system.
