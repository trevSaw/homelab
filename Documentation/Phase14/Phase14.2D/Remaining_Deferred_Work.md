# Phase 14.2D — Remaining Deferred Work

Explicitly deferred as of Phase 14.2D. **Status note:** Phase 14.3 (Knowledge
Platform) has since been **implemented and validated** (2026-08-09) — see
`Documentation/Phase14/Phase14.3/`. The list below is the historical Phase 14.2D
record.

## Phase 14.3 — Knowledge Platform (now implemented)

- Knowledge Service (ingestion, indexing, retrieval, knowledge enrichment)
- Embedding pipeline
- ChromaDB vector indexing
- Incremental indexing
- Retrieval APIs
- Basic RAG retrieval
- Event-driven indexing
- Production validation

## Phase 14.4 — Knowledge Graph

- Graphify integration (entity/relationship extraction, graph sync, visualization)
- Hybrid graph/vector retrieval where appropriate

## Phase 14.5 — Tool Platform

- Tool Service
- MCP integration
- Local tool execution
- External APIs
- Open WebUI integration
- Tool registry
- Tool permissions

## Phase 15 — Council & Intelligence

- Simulated Council structured prompting
- Selection / deliberation / synthesis wiring to Dynamics
- Contributor explainability
- Context Intelligence / assembly hardening

## Phase 16 — Automation & Autonomous Workflows

- Agent create/evaluate/terminate lifecycle
- Workflow orchestration under KORA / Hermes

## Explicitly not implemented (validation confirmed absent)

- Knowledge retrieval / search (scheduled Phase 14.3)
- Vector search / embeddings (scheduled Phase 14.3)
- Graphify / knowledge graphs (scheduled Phase 14.4)
- Open WebUI Knowledge integration (Phase 14.3+)
- Tool Runtime expansion / MCP (scheduled Phase 14.5)
- Council integration (scheduled Phase 15)
- Autonomous ingestion agents (scheduled Phase 16)
- Knowledge search / retrieval
- Memory retrieval on the chat path

## Maintenance (non-blocking, scheduled separately)

- FastAPI lifespan migration (`@app.on_event("startup")` → `lifespan`)
- Decision on malformed-YAML handling (fail-loud vs graceful degrade)
- Honcho deployment assets for repository-backed validation
