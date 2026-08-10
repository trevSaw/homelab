# Migration Mapping — KORA Runtime → Hermes-Based KORA

**Branch:** `phase14-hermes-runtime`
**Base:** `cf26e24` (Phase 14 final checkpoint)
**Status:** DESIGN — no implementation yet
**Date:** 2026-08-10

Disposition legend:
- **KEEP IN KORA** — stays KORA-owned (identity/intelligence/governance).
- **MOVE TO HERMES** — generic runtime mechanics delegated to Hermes.
- **WRAP HERMES** — KORA keeps policy; Hermes capability is used behind a KORA boundary.
- **REPLACE WITH HERMES** — Hermes-native feature supersedes the custom one.
- **DEPRECATE** — removed later, only after replacement verified (Stage 15).
- **FUTURE** — designed for, not implemented (Council, agents).
- **UNUSED** — already dormant in Phase 14; no migration action.

| Current component (Phase 14) | Location | Disposition | Notes |
|---|---|---|---|
| Chat API entry `/v1/chat/completions` | `Runtime/app/main.py` | MOVE TO HERMES (entry) → WRAP: KORA keeps `chat_completions` as the intelligence endpoint | Open WebUI talks to Hermes api_server; KORA endpoint becomes the Hermes→KORA delegate target. Do NOT delete; keep as KORA intelligence API. |
| `/v1/models` | `main.py` | MOVE TO HERMES | Hermes api_server serves `/v1/models` (`API_SERVER_MODEL_NAME=KORA`). |
| `/health`, `/` | `main.py` | KEEP IN KORA (KORA subsystem health); Hermes has its own `/health` | Both must remain accurate for their layer. |
| Classification (`classify`) | `main.py` | KEEP IN KORA | Core intelligence; no Hermes equivalent. |
| Strategy selection (`select_strategy`) | `main.py` | KEEP IN KORA | Core intelligence. |
| Context assembly (`assemble_context`) | `main.py` | KEEP IN KORA | Core intelligence. |
| Explainability (`explainability`, `kora` object) | `main.py` | KEEP IN KORA | Must survive end-to-end through Hermes. |
| Execute/Admin refusal (`_refusal_message`) | `main.py` | KEEP IN KORA | Governance; never Hermes config. |
| Ollama chat proxy (`ollama_chat`) | `main.py` | MOVE TO HERMES (model runtime) | Hermes provider = Ollama already. KORA keeps knowledge-embedding calls. |
| Ollama tags helper | `main.py` | MOVE TO HERMES | Superseded by Hermes `/v1/models`. |
| Event Bus (`event_bus.py`) | `Runtime/app/event_bus.py` | KEEP IN KORA | Internal KORA messaging; Hermes has its own internal plumbing. Do not couple. |
| Memory Runtime (`memory_runtime.py`) | `Runtime/app/` | KEEP IN KORA | Memory authority. |
| Approval Engine (`approval_engine.py`) | `Runtime/app/` | KEEP IN KORA | Approval authority. |
| Proposal repository (`proposal_repository.py`) | `Runtime/app/` | KEEP IN KORA | Proposal state. |
| Commit coordinator (`commit_coordinator.py`) | `Runtime/app/` | KEEP IN KORA | Approval→persistence. |
| Durable memory contract (`durable_memory.py`) | `Runtime/app/` | KEEP IN KORA | Memory contract. |
| Honcho adapter (`honcho_adapter.py`) | `Runtime/app/` | KEEP IN KORA | Honcho writes ONLY via KORA commit coordinator. Hermes honcho hook NOT used (avoid second writer). |
| Memory API routes | `main.py` | KEEP IN KORA | Scoped tokens retained. |
| Memory auth (`auth.py`) | `Runtime/app/` | KEEP IN KORA | Retained. |
| Knowledge service facade (`Knowledge/service.py`) | `Knowledge/` | KEEP IN KORA | Knowledge authority. |
| Ingestion (`ingestion/`) | `Knowledge/` | KEEP IN KORA | Production trigger gap unchanged. |
| Chunking | `Knowledge/chunking/` | KEEP IN KORA | |
| Embeddings (Ollama provider) | `Knowledge/embedding/` | KEEP IN KORA | KORA embedding policy. |
| Chroma adapter | `Knowledge/storage/chroma.py` | KEEP IN KORA | Infrastructure, not SoT. |
| Index metadata store | `Knowledge/storage/index_metadata.py` | KEEP IN KORA | |
| Indexing coordinator | `Knowledge/indexing/` | KEEP IN KORA | |
| Retrieval service | `Knowledge/retrieval/` | KEEP IN KORA | |
| Context assembly (knowledge) | `Knowledge/context/` | KEEP IN KORA | |
| Graph store (SQLite) | `Knowledge/graph/sqlite_store.py` | KEEP IN KORA | |
| Graph extraction | `Knowledge/graph/extraction.py` | KEEP IN KORA | |
| Graph retrieval | `Knowledge/graph/retrieval.py` | KEEP IN KORA | |
| Combined retrieval | `Knowledge/graph/combined.py` | KEEP IN KORA | |
| Graph export + Graphify client | `Knowledge/graph/export.py`, `graphify.py` | KEEP IN KORA | Graphify = serve layer only (unchanged known behavior). |
| Tool registry | `Tools/registry/` | KEEP IN KORA | Registry of known tools remains KORA-owned. |
| Tool authorization | `Tools/auth/` | KEEP IN KORA | Governance. |
| Tool executor | `Tools/executor/` | WRAP HERMES | Execution may delegate to Hermes-native tool execution; KORA executor retained as fallback until verified. |
| Generic MCP client | `Tools/mcp/client.py` | MOVE TO HERMES (evaluate) | Hermes has mature native MCP client. KORA's Graphify client still uses it for graph (KEEP). |
| MCP tool provider | `Tools/providers/mcp.py` | MOVE TO HERMES (evaluate) | No MCP servers configured today; no functional loss. |
| Ollama local tools (`ollama.list_models/running`) | `Tools/providers/local/ollama.py` | REPLACE WITH HERMES (evaluate) | Hermes has native Ollama/status tooling; confirm parity before removal. |
| Tool platform facade (`platform.py`) | `Tools/platform.py` | KEEP IN KORA (policy) / WRAP | KORA keeps decision authority. |
| Tool config (`tools.yaml`) | `Config/tools.yaml` | KEEP IN KORA | Authoritative tool inventory. |
| Runtime config (`runtime.yaml`) | `Config/runtime.yaml` | KEEP IN KORA | KORA policy config. |
| Council registration | `Config/council_registration.yaml` | KEEP IN KORA | Conceptual solo only. |
| Hermes registration | `Config/hermes_registration.yaml` | KEEP IN KORA (update) | Reconcile with new architecture (Stage 16). |
| KORA prompts (`solo_system.txt`) | `Prompts/` | KEEP IN KORA → reuse as Hermes persona source | Identity text must be carried into Hermes system prompt verbatim (config-only). |
| Tests | `Runtime/tests`, `Knowledge/tests`, `Tools/tests` | KEEP IN KORA | Regression suite retained; new Hermes-path tests added (Stage 14). |
| Dockerfile (kora) | `Runtime/Dockerfile` | KEEP IN KORA | KORA container still needed (intelligence + subsystems). |
| Compose (kora) | `services/kora/compose.yaml` | KEEP, network-adjusted | KORA removed from proxy net; reachable by Hermes. |
| Compose (hermes) | `services/hermes/compose.yaml` | UPDATE | Enable api_server platform (API_SERVER_KEY/PORT), KORA persona model name, delegation to KORA. |
| Open WebUI compose | `services/open-webui/compose.yaml` | UPDATE | Point `OPENAI_API_BASE_URL` at `http://hermes:8642/v1`. |
| Council (Phase 15) | n/a | FUTURE | No implementation now. |
| Agents / autonomous workflows (Phase 16) | n/a | FUTURE | Hermes agent lifecycle enables later. |
