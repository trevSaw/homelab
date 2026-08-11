# Honcho ↔ Hermes Connectivity Fix

**Date:** 2026-08-11
**Scope:** Enable the native Hermes Honcho memory provider (`memory.provider: honcho`) against the self-hosted Honcho v3.0.10 instance.
**Status:** Connectivity verified; dialectic performance outstanding (separate model/runtime decision).

---

## 1. Problem

Hermes v0.17.0 ships a native Honcho memory provider and was already configured for it
(`memory.provider: honcho` + `$HERMES_HOME/honcho.json` → `http://honcho-api:8000`),
but Honcho's backend was failing on every provider call:

- **Dialectic / Dream LLM calls** defaulted to OpenAI `gpt-5.4-mini`; with only a dummy
  `LLM_OPENAI_API_KEY` set, Honcho raised `AuthenticationError` on every `.chat()` —
  Hermes logged `Honcho dialectic query failed: An unexpected error occurred`.
- **Embedding dimension mismatch**: Honcho's pgvector schema and `EMBEDDING_VECTOR_DIMENSIONS`
  defaulted to `1536`, but the configured `nomic-embed-text` model returns `768` dims.
  The deriver crashed on every embed (`ValueError: Embedding dimension mismatch ...
  Expected 1536, got 768`) and crash-looped at startup once the dimension was corrected.

## 2. Changes

### 2.1 Honcho `.env` — `/mnt/monarch/appdata/honcho/.env`

Appended the following, mirroring the existing DERIVER/SUMMARY pattern (all LLM text-gen
features now route through the local Ollama `qwen3:8b` endpoint instead of OpenAI defaults):

```bash
EMBEDDING_VECTOR_DIMENSIONS=768

# Dialectic (per reasoning level)
DIALECTIC_LEVELS__MINIMAL__MODEL_CONFIG__TRANSPORT=openai
DIALECTIC_LEVELS__MINIMAL__MODEL_CONFIG__MODEL=qwen3:8b
DIALECTIC_LEVELS__MINIMAL__MODEL_CONFIG__OVERRIDES__BASE_URL=http://ollama:11434/v1
DIALECTIC_LEVELS__LOW__MODEL_CONFIG__TRANSPORT=openai
DIALECTIC_LEVELS__LOW__MODEL_CONFIG__MODEL=qwen3:8b
DIALECTIC_LEVELS__LOW__MODEL_CONFIG__OVERRIDES__BASE_URL=http://ollama:11434/v1
DIALECTIC_LEVELS__MEDIUM__MODEL_CONFIG__TRANSPORT=openai
DIALECTIC_LEVELS__MEDIUM__MODEL_CONFIG__MODEL=qwen3:8b
DIALECTIC_LEVELS__MEDIUM__MODEL_CONFIG__OVERRIDES__BASE_URL=http://ollama:11434/v1
DIALECTIC_LEVELS__HIGH__MODEL_CONFIG__TRANSPORT=openai
DIALECTIC_LEVELS__HIGH__MODEL_CONFIG__MODEL=qwen3:8b
DIALECTIC_LEVELS__HIGH__MODEL_CONFIG__OVERRIDES__BASE_URL=http://ollama:11434/v1
DIALECTIC_LEVELS__MAX__MODEL_CONFIG__TRANSPORT=openai
DIALECTIC_LEVELS__MAX__MODEL_CONFIG__MODEL=qwen3:8b
DIALECTIC_LEVELS__MAX__MODEL_CONFIG__OVERRIDES__BASE_URL=http://ollama:11434/v1

# Dream (consolidation)
DREAM_DEDUCTION_MODEL_CONFIG__TRANSPORT=openai
DREAM_DEDUCTION_MODEL_CONFIG__MODEL=qwen3:8b
DREAM_DEDUCTION_MODEL_CONFIG__OVERRIDES__BASE_URL=http://ollama:11434/v1
DREAM_INDUCTION_MODEL_CONFIG__TRANSPORT=openai
DREAM_INDUCTION_MODEL_CONFIG__MODEL=qwen3:8b
DREAM_INDUCTION_MODEL_CONFIG__OVERRIDES__BASE_URL=http://ollama:11434/v1
```

Containers recreated via `docker compose up -d` from `/mnt/monarch/appdata/honcho`.

### 2.2 pgvector schema — resize to 768

With `EMBEDDING_VECTOR_DIMENSIONS=768` the API/deriver startup validator refused to start
against the existing `vector(1536)` columns. Resized (data negligible: 0 docs, 4 message
embeddings) using Honcho's bootstrap script in a one-off container on `ollama_ollama-net`:

```bash
docker run --rm --network ollama_ollama-net \
  -e DB_CONNECTION_URI='postgresql+psycopg://postgres:<pw>@database:5432/postgres' \
  -e EMBEDDING_VECTOR_DIMENSIONS=768 \
  -e EMBEDDING_MODEL_CONFIG__TRANSPORT=openai \
  -e EMBEDDING_MODEL_CONFIG__MODEL=nomic-embed-text \
  -e EMBEDDING_MODEL_CONFIG__OVERRIDES__BASE_URL=http://ollama:11434/v1 \
  honcho-api:latest /app/.venv/bin/python scripts/configure_embeddings.py --yes
```

Effect: `ALTER COLUMN ... TYPE vector(768) USING NULL` on `public.documents.embedding` and
`public.message_embeddings.embedding`, HNSW indices dropped and recreated.

### 2.3 Hermes `honcho.json` — `/mnt/monarch/appdata/hermes/honcho.json`

Raised the provider's HTTP timeout and lowered dialectic cost so slow local LLM responses
stop aborting:

```json
{
  "baseUrl": "http://honcho-api:8000",
  "workspace": "kora",
  "peerName": "user",
  "aiPeer": "kora",
  "enabled": true,
  "timeout": 180,
  "dialecticDepth": 1,
  "dialecticCadence": 5,
  "dialecticReasoningLevel": "minimal"
}
```

> **Not yet live.** Hermes was intentionally **not restarted** (production KORA gateway;
> another user active on Ollama/Open WebUI). The running gateway still holds the previous
> client (30s timeout). The change takes effect on next Hermes restart.

## 3. Verification

Performed from inside the `hermes` container using the installed honcho-ai SDK
(`/opt/data/honcho-libs`, the exact library the provider uses):

| Check | Result |
|---|---|
| `GET http://honcho-api:8000/health` from hermes | `{"status":"ok"}` |
| `from honcho import Honcho` in hermes venv | OK |
| Peer create/get (workspace `kora`) | OK |
| Session create/list | OK |
| Message add | OK |
| Session `context(summary=True)` | OK — summary returned |
| Deriver | no longer crash-looping; embeddings at dim 768 |
| Dialectic `.chat()` | **slow — exceeds client timeout on CPU-bound Ollama** |

## 4. Outstanding (deliberately not addressed)

- **Dialectic performance.** Honcho's dialectic `.chat()` runs an agentic tool loop on
  `qwen3:8b`, which is CPU-bound in Ollama (host GPU — NVIDIA T400 4 GB — is not passed to
  the Ollama container, and the 8B model exceeds its 4 GB VRAM). A single bare LLM call
  took ~53 s; multi-round dialectic exceeds even 180 s. This is a **model/runtime selection
  decision** (which model, GPU pass-through, smaller quant, etc.), not a Honcho architecture
  problem — see decision to be made separately.
- **Hermes restart** to load the new `honcho.json` timeout/tuning.
- The pre-existing Phase 14 final migration to `services/hermes/compose.yaml` and the
  `honcho-ai` install command are tracked separately and were **not** part of this change.

## 5. Files touched

| Path | Where | Change |
|---|---|---|
| `/mnt/monarch/appdata/honcho/.env` | host SoT | dialectic + dream model config; `EMBEDDING_VECTOR_DIMENSIONS=768` |
| pgvector `public.documents` / `public.message_embeddings` | honcho-postgres | `vector(1536)` → `vector(768)` |
| `/mnt/monarch/appdata/hermes/honcho.json` | host SoT | `timeout: 180`, dialectic tuning (not yet live) |
| `services/honcho/compose.yml` | repo mirror | unchanged (matches host) |
