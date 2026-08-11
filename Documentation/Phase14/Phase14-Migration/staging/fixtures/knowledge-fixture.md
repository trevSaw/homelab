# Homelab Architecture — Knowledge Fixture

This file is a staging knowledge fixture ingested through the REAL KORA
ingestion pipeline (ingest → version → chunk → Ollama embedding → in-memory
vector store) to exercise provenance-aware retrieval in the prototype.

## Server Inventory

The homelab primary server is named **mocha**. It hosts the KORA runtime
container, the Hermes agent container, and the Open WebUI container on the
shared Docker networks.

## Services

- **KORA** — the homelab AI conductor. Owns identity, governance, memory
  policy, and knowledge policy.
- **Hermes** — generic agent runtime substrate (ADR-0004).
- **Ollama** — local inference backend (qwen3 models).
- **Open WebUI** — user interface only (ADR-0008).

## Standards

- Memory ≠ Knowledge ≠ Tools.
- Execute and Administrative actions are refused by KORA governance.
- Explainability and provenance are required on every KORA response.
