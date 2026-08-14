# KORA Personal Knowledge Archive

**Status:** Canonical curated personal/project knowledge for KORA (Phase 17).
**Maintained by:** Trevor (primary KORA user).
**Source:** ChatGPT history (historical) + existing project documentation.
**Ingestion:** NOT yet ingested into Chroma/Honcho/Graphify — later, separately approved.

> **Purpose.** This is the curated, human-readable representation of what KORA
> should know about the user and their history. Raw ChatGPT conversations are
> historical evidence kept under `ChatGPT_History/`; they are not converted
> wholesale into durable memory. Information in this archive is organized by
> topic, distinguishes current vs historical facts, and marks superseded
> decisions rather than deleting them.
>
> **Source of truth rule.** Facts below are limited to what is explicitly
> supported by the repository and project documentation. Personal sections not
> yet populated are marked `[PENDING USER INPUT]` — they are filled when the
> user provides their personal knowledge material. Do not infer unstated
> personal facts.

---

## 1. About Me

- **Name:** Trevor (primary KORA user).
- **Role in project:** Owner / operator of the homelab and the Brainiac/KORA
  AI platform; admin account in Open WebUI.
- **Contact (from account):** `tsawyerm@gmail.com` (Open WebUI admin account).
- **Household:** Trevor (primary user, has KORA access) and Tracy (partner,
  has restricted Open WebUI access — no KORA; permitted Ollama models only).
- `[PENDING USER INPUT]` — additional biography, background, interests.

## 2. Preferences

`[PENDING USER INPUT]` — general preferences not yet provided.

## 3. Communication / AI Preferences

- KORA is presented as **KORA** (Brainiac) from the user's perspective; the
  Open WebUI model/display name is `KORA`.
- `[PENDING USER INPUT]` — preferred tone, style, verbosity, etc.

## 4. Life Context

`[PENDING USER INPUT]` — life context not yet provided.

## 5. Work and Professional Context

`[PENDING USER INPUT]` — work context not yet provided.

## 6. Technical Environment

### Homelab
- Self-hosted homelab managed via Docker Compose under documented governance
  (Docker standard, service ownership, network/volume ownership).
- Production data root: `/mnt/monarch/appdata/<service>`.
- Public-facing domain: `fatherfankscloud.uk` (Traefik ingress; e.g.,
  `chat.fatherfankscloud.uk` = Open WebUI, `hermes.fatherfankscloud.uk` =
  Hermes dashboard).
- External networks: `ollama_ollama-net`, `proxy`, `ai-assistant` (governed).

### Computers / Hardware
- Inference runs on a machine with an NVIDIA T400 4 GB GPU available but **not**
  currently passed through to Ollama (Ollama inference is CPU-bound).
- `[PENDING USER INPUT]` — full hardware inventory not yet provided.

### Networking
- Traefik reverse proxy with Let's Encrypt TLS; all internal services bound to
  `127.0.0.1` where production-oriented; external exposure via Traefik routes.

### Docker / Services
- Governed Compose stacks under `services/` (each service has README, .env
  gitignored, healthchecks, restart policies, resource limits, labels).
- Persistent data on `/mnt/monarch/appdata/`; no ad-hoc `docker run` containers.

### AI / LLM Infrastructure
- **Ollama** — local inference backend (`http://ollama:11434/v1`); models
  include `qwen3:8b`, `gpt-oss:20b-cloud`, `gemma3:*`, `qwen2.5-coder:7b`, and
  others.
- **Open WebUI** — UI (`chat.fatherfankscloud.uk`); user/model access control
  (Trevor admin; Tracy restricted).
- **Hermes v0.17.0** — generic agent/runtime platform (api_server :8642);
  hosts the KORA head agent.
- **Honcho v3.0.10** — canonical personal memory (native Hermes provider,
  workspace `kora`, peer `user`, `pinUserPeer: true`).
- **Chroma** (`kora-chromadb`) — canonical knowledge/RAG store.
- **Graphify** — canonical relationship/knowledge-graph service (MCP).
- **MCP (Hermes-native)** — tool mechanism (Graphify + Context7 + jDocMunch).

## 7. Brainiac / KORA

### Brainiac
- **Brainiac** is the primary AI entity of the homelab; **KORA** is Brainiac
  (the name KORA is used as the product identity). See
  `Architecture/ai/KORA.md`.

### KORA
- **KORA** = Knowledge-Oriented Response Assistant; the homelab AI conductor /
  head intelligence agent.
- **Current:** KORA is a **Hermes-hosted agent** (head intelligence/governance
  agent hosted inside Hermes). It is **not** a standalone runtime/container.
- **Historical:** KORA previously ran as a standalone KORA Runtime (FastAPI,
  custom orchestration) — superseded during Phase 14.

### Architecture
```text
Open WebUI → Hermes → KORA HEAD AGENT → Honcho / Chroma / Graphify / Ollama / MCP
```
- Canonical ownership: Open WebUI = UI; Hermes = runtime; KORA = head agent;
  Honcho = personal memory; Chroma = knowledge/RAG; Graphify = relationships;
  Ollama = inference; MCP = tools.

### Governance
- Read-only MCP tool allowlists (`tools.include`); no destructive/admin tools
  enabled; "existence of a tool ≠ authorization".
- User isolation: KORA is Trevor-only; Tracy sees only permitted Ollama models.

### Memory
- **Honcho** is the canonical personal-memory backend (native Hermes provider).
- The retired custom Phase 14.2 Memory Runtime is **not** part of the final
  architecture.

### Knowledge
- **Chroma** (`kora-chromadb`) is the canonical knowledge/RAG platform.
- Context7 (live external library docs) and jDocMunch (local Brainiac docs) are
  retrieval tools, not replacements for the Knowledge Platform.

### Tools
- **Hermes-native MCP**: Graphify (7 read-only graph tools), Context7
  (`resolve-library-id`, `query-docs`), jDocMunch (7 read-only local-doc tools).

### Hermes
- Hermes v0.17.0, upstream/unmodified (no fork). api_server exposes model
  `KORA`; KORA's chat model is Hermes `model.default` (currently
  `gpt-oss:20b-cloud`).

### Ollama
- Inference backend. KORA's model is `gpt-oss:20b-cloud` (structured MCP
  tool-call capable); `qwen3:8b` was the prior model (CPU-bound, did not emit
  structured tool calls reliably in the full Hermes context).

## 8. Projects

- **Brainiac / KORA** — the homelab AI platform (KORA head agent + Council
  future + Hermes runtime + Honcho/Chroma/Graphify/Ollama/MCP).
- **Homelab infrastructure** — governed Docker Compose service stacks
  (`services/`), Traefik, storage at `/mnt/monarch`.
- `[PENDING USER INPUT]` — other personal/professional projects.

## 9. Major Decisions

### Decision: KORA runtime model — standalone runtime → Hermes-hosted agent
- **Decision:** KORA became a Hermes Agent hosted inside Hermes v0.17.0.
- **Date/Phase:** Phase 14 (final; retirement of standalone KORA Runtime,
  2026-08-11).
- **Reason:** Simplify the architecture; use Hermes as the generic agent
  runtime rather than a custom KORA runtime; no Hermes fork.
- **Current Status:** Current.
- **Supersedes:** The standalone KORA Runtime (retired; preserved in git).
- **Notes:** Old runtime kept recoverable via git history + backup.

### Decision: Memory backend — custom Memory Runtime → Honcho
- **Decision:** Honcho is the canonical personal-memory backend (native Hermes
  honcho provider).
- **Date/Phase:** Phase 14 (final).
- **Reason:** Hermes ships a native Honcho integration; the custom Phase 14.2
  Memory Runtime was redundant for ordinary personalization memory.
- **Current Status:** Current.
- **Supersedes:** Custom Phase 14.2 Memory Runtime / Approval Engine / Event
  Bus (retired from active architecture).
- **Notes:** Workspace `kora`, peer `user`, `pinUserPeer: true`.

### Decision: KORA inference model — qwen3:8b → gpt-oss:20b-cloud
- **Decision:** KORA's chat model is `gpt-oss:20b-cloud` (Hermes
  `model.default`).
- **Date/Phase:** Phase 16 (2026-08-12).
- **Reason:** `gpt-oss:20b-cloud` produces genuine structured MCP tool calls;
  `qwen3:8b` emitted them as text JSON in the full Hermes context and is
  CPU-bound.
- **Current Status:** Current.
- **Supersedes:** `qwen3:8b` as KORA's model.
- **Notes:** Honcho dialectic/dream models are independently configured
  (Honcho env) and remain decoupled from KORA's chat model.

### Decision: Tools — Hermes-native MCP with explicit allowlists
- **Decision:** MCP servers (Graphify, Context7, jDocMunch) exposed to KORA via
  Hermes-native `mcp_servers` with explicit `tools.include` allowlists.
- **Date/Phase:** Phase 16 / 16.x.
- **Reason:** Use Hermes's native MCP rather than custom tool infra; read-only
  first; least privilege.
- **Current Status:** Current.
- **Supersedes:** None.
- **Notes:** Docker MCP rejected (docker-socket); Proxmox rejected (no
  Proxmox); jCodeMunch/jDataMunch/GitHub/Filesystem deferred pending
  prerequisites.

## 10. Completed Work

- **Phase 14** — KORA + Hermes production architecture (COMPLETE): Hermes-hosted
  KORA; Honcho native memory; Chroma knowledge; Graphify relationships; Ollama
  inference; Open WebUI UI; standalone KORA Runtime retired.
- **Phase 15** — Council foundation (FOUNDATION COMPLETE — **PAUSED**): Council
  content preserved; Hermes-native `delegate_task` mechanism established; no
  deployment.
- **Phase 16** — MCP / Tools (COMPLETE): model switch to `gpt-oss:20b-cloud`;
  Graphify + Context7 + jDocMunch MCP tools verified end-to-end; governance
  (read-only allowlists).
- **Phase 17** — Personal Knowledge Migration (**STARTED** — curation):
  archive created; ingestion pending.

## 11. Current Plans

- Complete the Personal Knowledge Archive with user-supplied material.
- (Later) Design the Phase 17 ingestion pipeline (which archive content →
  Chroma corpus; which facts → Honcho memory; relationships → Graphify).

## 12. Future Plans

- **Phase 15 (Council)** — resume only on explicit request (currently paused).
- **Automation / autonomous workflows** — deferred (forward-looking design).
- Further MCP/tool expansion as prerequisites are met.

## 13. Goals

`[PENDING USER INPUT]` — personal goals not yet provided. (Project-level: a
coherent, governed homelab AI platform with KORA as the head intelligence.)

## 14. Lessons Learned

- Custom runtimes (KORA Runtime, Memory Runtime, orchestration layers) tend to
  add complexity beyond their value — prefer capabilities already provided by
  the platform (Hermes) and canonical services.
- A smaller MCP stack is better than unnecessary infrastructure; explicit
  allowlists over wholesale exposure.
- Model selection matters for agent behavior (structured tool calls).
- Preserve historical work (git, backups) rather than deleting.

## 15. Important Historical Context

- KORA was originally a standalone FastAPI runtime with custom Knowledge/Tool/
  Memory platforms (Phase 14.1–14.5), later retired in favor of
  Hermes-hosted KORA.
- The custom Phase 14.2 Memory Runtime (approval-gated proposals, Event Bus)
  was evaluated and retired in favor of native Honcho.
- A Cloudflare DNS API token leaked in an old commit (`b258fac`,
  `Validation/Phase11/traefik/inspect/`); the Phase 14+ branches were pushed
  redacted; the old branches remain local-only pending a decision.

## 16. Superseded / Historical Decisions

### Standalone KORA Runtime
- **Current:** KORA runs as a Hermes-hosted agent.
- **Historical:** KORA previously used a standalone runtime (FastAPI,
  `services/kora`, `homelab/kora-runtime` image).
- **Status:** Superseded during Phase 14 (retired 2026-08-11).

### Custom Memory Runtime (Phase 14.2)
- **Current:** Honcho is the canonical memory backend.
- **Historical:** Approval-gated custom Memory Runtime / Event Bus / Approval
  Engine / Honcho adapter lived in the KORA process.
- **Status:** Superseded during Phase 14 (retired from active architecture).

### KORA inference model qwen3:8b
- **Current:** `gpt-oss:20b-cloud`.
- **Historical:** `qwen3:8b`.
- **Status:** Superseded during Phase 16 (2026-08-12).

### Hermes role (Phase 14.1 "thin execution layer")
- **Current:** Hermes is the generic agent runtime hosting KORA.
- **Historical:** Hermes was described as a thin/optional layer not on the
  primary chat path.
- **Status:** Superseded by the Phase 14 final architecture.

## 17. Project Relationships

Human-readable contextual relationships (Graphify remains the operational
relationship store; this section is for KORA context):

- **Brainiac → KORA** — KORA is Brainiac (product identity).
- **KORA → Hermes** — KORA is a Hermes-hosted agent; Hermes is the runtime.
- **KORA → Honcho** — Honcho is KORA's personal memory (native provider).
- **KORA → Chroma** — Chroma is KORA's knowledge/RAG platform.
- **KORA → Graphify** — Graphify is KORA's relationship/graph service.
- **KORA → MCP** — Hermes-native MCP provides tools (Graphify, Context7,
  jDocMunch).
- **KORA → Ollama** — Ollama provides inference (`gpt-oss:20b-cloud`).
- **Phase 14 → Hermes migration** — standalone KORA Runtime retired; KORA became
  a Hermes agent.
- **Phase 15 → Council** — Council foundation (paused); members NOVA, IRIS,
  TALIA, SOLA, LUMA, ALUMA, NOMA.
- **Phase 16 → MCP/Tools** — model switch + governed MCP tool set.
- **Phase 17 → Personal Knowledge Migration** — curated archive → later Chroma
  corpus + selective Honcho memory.

---

*End of KORA Personal Knowledge Archive. Sections marked `[PENDING USER INPUT]`
are filled when the user provides personal knowledge material.*
