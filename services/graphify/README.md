# Graphify — Knowledge Graph serve layer (Phase 14.4)

Graphify serves KORA's derived Knowledge graph over MCP Streamable HTTP. It is a
relationship graph (entities, edges, traversal, visualization) — NOT the Knowledge
authority and NOT a vector store.

## Deploy

```bash
cd services/graphify
cp .env.example .env        # set GRAPHIFY_API_KEY
docker compose build
docker compose up -d
```

## Stop

```bash
cd services/graphify
docker compose down          # do NOT use -v (persists graph data on host)
```

## Update

```bash
cd services/graphify
docker compose build --pull
docker compose up -d
```

## Persistence

Graphify serves the graph read-only from the host path `/mnt/monarch/appdata/kora`
(mounted at `/data`), the same path KORA mounts as `/data`. KORA exports its
derived graph to `/data/graph.json`; Graphify reads it. Graph data is never stored
inside the container filesystem.

## Docker network

Uses the external `ollama_ollama-net` network so KORA can reach it at
`http://graphify:8080`.

## KORA connectivity

KORA connects via `KORA_GRAPHIFY_BASE_URL=http://graphify:8080` (see
`services/kora/.env.example`).

## Health check

`POST /mcp` with a JSON-RPC `initialize` request; the container healthcheck uses
this and reports `healthy` when Graphify is serving.

## Image

`homelab/graphify:14.4.0` — built from the pinned upstream source (Graphify
0.9.37 / v8, commit `09a34ad`), including the Streamable HTTP transport and
`--json-response`.
