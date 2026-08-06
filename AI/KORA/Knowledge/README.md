# Knowledge domain for KORA

This directory contains the foundation for Knowledge ingestion.

- **KnowledgeDocument** – immutable representation of a knowledge source.
- **Ingestion pipeline** – reads local files, creates a document, extracts minimal metadata, and stores it via a pluggable `KnowledgeStore`.
- **Storage abstraction** – `KnowledgeStore` protocol defines async CRUD operations; an in‑memory implementation is provided for tests.
- **EventBus integration** – ingestion publishes events on the `knowledge.*` namespace using the shared internal `EventBus`.

All services are internal Python components; no HTTP endpoints are exposed at this stage.
