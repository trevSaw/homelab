# Staging Proof Report — Hermes v0.17.0 API Server (empirical)

**Branch:** `phase14-hermes-runtime`
**Date:** 2026-08-10
**Status:** PROOF COMPLETE — the primary design premise was falsified; see §5.
**Scope:** isolated staging container (`hermes-staging`), own data dir, port
`127.0.0.1:18642`, image `nousresearch/hermes-agent:latest` (v0.17.0). No
production container or data was touched. Container torn down after the test.

## 1. Setup

- Image: `nousresearch/hermes-agent:latest` = **Hermes Agent v0.17.0**.
- Enabled the OpenAI-compatible API server platform via env:
  `API_SERVER_ENABLED=true`, `API_SERVER_KEY=staging-test-key`,
  `API_SERVER_MODEL_NAME=KORA`, `API_SERVER_PORT=8642`.
- Model: Ollama `qwen3:14b` (provider custom → `http://ollama:11434/v1`).
  Required overrides in `config.yaml`: `model.context_length: 131072` and
  `model.ollama_num_ctx: 65536` (Hermes enforces a 64K context minimum for its
  agent tooling; Ollama reports 40K by default).

## 2. Results

| Probe | Result |
|---|---|
| `GET /health` | ✅ `{"status":"ok","platform":"hermes-agent","version":"0.17.0"}` |
| `GET /v1/models` (Bearer) | ✅ returns model **`KORA`** (`owned_by: hermes`) |
| `GET /v1/models` (no auth) | ✅ HTTP 401 (API server refuses to run without `API_SERVER_KEY`) |
| `POST /v1/chat/completions` | ✅ OpenAI-format response (`object: chat.completion`, `id: chatcmpl-…`, `model: KORA`) |
| System prompt honored? | ✅ exact-echo probe returned `KORA-IDENTITY-TEST` verbatim |
| Identity stability | ⚠️ a cold-start response said "I am Qwen" despite the KORA system prompt — identity is **model-enforced prompt**, not structural |
| **`kora` explainability object** | ❌ **ABSENT.** Response keys: `choices, created, id, model, object, usage`. No classification, no stores_queried/skipped, no provenance. |
| Internal agent loop | ✅ `api_server` runs the full `AIAgent` loop (`run_agent.py`); **no passthrough/proxy mode** to an external composer exists. |
| Delegation | ✅ native but is **subagent tool-call delegation** (`delegate_task`), not a per-turn proxy to a KORA composer. |

## 3. What this proves

- Hermes **can** be an OpenAI-compatible entry for Open WebUI, advertise the
  model as `KORA`, and enforce `API_SERVER_KEY` auth. ✅
- Hermes **cannot** natively reproduce KORA's response composer: no `kora`
  explainability object, no KORA `classify → strategy → assemble → explain`
  pipeline, and KORA identity is prompt-only (weaker than the structural
  `kora.identity: KORA` in the current runtime). ❌

## 4. What this means for the migration

The primary design in `01-target-architecture.md` §0 assumed the Hermes agent
could delegate the *intelligence turn* to KORA and return KORA's composed
response with explainability intact. **That is not what Hermes does.** Hermes
generates its own agent response; there is no per-turn passthrough to a KORA
composer. Options:

- **(a) Hermes as a KORA-branded agent**: KORA identity + governance as a
  system prompt, KORA Memory/Knowledge/Tools attached as MCP/tools. Loses the
  structural `kora` explainability object and the KORA classify/strategy
  logic unless re-encoded inside Hermes (i.e., recreating KORA capability in
  Hermes — explicitly discouraged by the migration rules).
- **(b) Hermes as pure entry, KORA as composer**: requires a custom Hermes
  hook/plugin to relay `/v1/chat/completions` to KORA and return its response
  verbatim. That is *custom runtime maintenance* — the opposite of the
  migration's stated purpose ("reduce custom runtime maintenance").
- **(c) Reconsider the architecture** (see §5).

## 5. Recommendation (per migration safety rules)

Per the task's rule — *"If Hermes cannot provide a required capability: STOP
and report it. Do not recreate the same capability inside KORA merely to force
the migration through"* — the migration should **not** proceed to the
production cutover (Stage 9+) on the current design. The Hermes stack is a
capable agent runtime, but it does not provide the one capability the target
architecture depends on: passing the composed response through KORA's
governed, explainable intelligence layer. A decision is required before any
further implementation (see next report section).
