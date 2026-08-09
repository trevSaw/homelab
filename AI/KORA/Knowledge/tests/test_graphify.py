"""Tests for the Graphify HTTP MCP client and the graph export to Graphify format."""

import asyncio
import json

import httpx

from ..graph.graphify import GraphifyClient, GraphifyError, GraphifyUnavailableError
from ..graph.export import build_graphify_document, export_to_graphify
from ..graph.in_memory_store import InMemoryGraphStore
from ..graph.models import GraphEntity, GraphRelationship, entity_id, relationship_id


class _GraphifyMCPHandler(httpx.MockTransport):
    def __init__(self, *, fail: bool = False) -> None:
        super().__init__(handler=self._handler)
        self._fail = fail
        self.session_id = "sess-1"
        self.calls = []

    def _handler(self, request: httpx.Request) -> httpx.Response:
        if self._fail:
            raise httpx.ConnectError("graphify down")
        payload = json.loads(request.content)
        method = payload.get("method")
        if method == "initialize":
            return httpx.Response(
                200,
                headers={"mcp-session-id": self.session_id},
                json={
                    "jsonrpc": "2.0",
                    "id": payload.get("id"),
                    "result": {
                        "protocolVersion": "2025-03-26",
                        "capabilities": {},
                        "serverInfo": {"name": "graphify", "version": "0.9.37"},
                    },
                },
            )
        if method == "notifications/initialized":
            return httpx.Response(202, json={})
        if method == "tools/call":
            self.calls.append(payload)
            name = payload.get("params", {}).get("name")
            if name == "get_node":
                text = "Node: Memory Service\n  ID: e1\n  Source: docs/memory.md L1\n  Type: document"
            elif name == "get_neighbors":
                text = "Neighbors of Memory Service:\n  --> Knowledge Service [references] [EXTRACTED]"
            elif name == "shortest_path":
                text = "Shortest path (2 hops):\n  A --references--> B"
            elif name == "graph_stats":
                text = "Nodes: 10, Edges: 12"
            elif name == "query_graph":
                text = "Traversal: BFS depth=3 | Start: [Memory] | 3 nodes found"
            else:
                text = "ok"
            return httpx.Response(
                200,
                json={
                    "jsonrpc": "2.0",
                    "id": payload.get("id"),
                    "result": {"content": [{"type": "text", "text": text}]},
                },
            )
        return httpx.Response(200, json={"jsonrpc": "2.0", "id": payload.get("id"), "result": {}})


def _client(handler: _GraphifyMCPHandler) -> GraphifyClient:
    return GraphifyClient(base_url="http://graphify:8080", api_key="test-key", transport=handler)


def test_graphify_health():
    handler = _GraphifyMCPHandler()
    client = _client(handler)
    assert asyncio.run(client.health()) is True
    asyncio.run(client.close())


def test_graphify_get_node():
    handler = _GraphifyMCPHandler()
    client = _client(handler)
    text = asyncio.run(client.get_node("Memory Service"))
    assert "Node: Memory Service" in text
    asyncio.run(client.close())


def test_graphify_query_graph_and_neighbors():
    handler = _GraphifyMCPHandler()
    client = _client(handler)
    q = asyncio.run(client.query_graph("how does auth work"))
    assert "Traversal" in q
    n = asyncio.run(client.get_neighbors("Memory Service"))
    assert "Neighbors" in n
    asyncio.run(client.close())


def test_graphify_unavailable_raises():
    client = _client(_GraphifyMCPHandler(fail=True))
    try:
        asyncio.run(client.get_node("x"))
        assert False, "expected GraphifyUnavailableError"
    except GraphifyUnavailableError:
        pass
    asyncio.run(client.close())


def test_graphify_auth_rejected():
    class AuthHandler(httpx.MockTransport):
        def __init__(self) -> None:
            super().__init__(handler=self._handler)

        def _handler(self, request: httpx.Request) -> httpx.Response:
            return httpx.Response(401, json={"error": "unauthorized"})

    client = GraphifyClient(base_url="http://graphify:8080", api_key="bad", transport=AuthHandler())
    try:
        asyncio.run(client.get_node("x"))
        assert False, "expected GraphifyError"
    except GraphifyError:
        pass
    asyncio.run(client.close())


def _seed_store() -> InMemoryGraphStore:
    store = InMemoryGraphStore()
    a = GraphEntity(
        entity_id=entity_id("memory-service", "document"),
        entity_type="document",
        canonical_name="memory-service",
        source_knowledge_id="k1",
        source_version="v1",
        source_content_hash="h1",
        source_ref="/docs/memory.md",
    )
    b = GraphEntity(
        entity_id=entity_id("knowledge-service", "document"),
        entity_type="document",
        canonical_name="knowledge-service",
        source_knowledge_id="k2",
        source_version="v1",
        source_content_hash="h2",
        source_ref="/docs/knowledge.md",
    )
    store.upsert_entity(a)
    store.upsert_entity(b)
    store.upsert_relationship(
        GraphRelationship(
            relationship_id=relationship_id(a.entity_id, "references", b.entity_id),
            source_entity=a.entity_id,
            relationship_type="references",
            target_entity=b.entity_id,
            source_knowledge_id="k1",
            confidence="EXTRACTED",
        )
    )
    return store


def test_export_produces_graphify_node_link_document():
    doc = build_graphify_document(_seed_store())
    assert doc["directed"] is False
    assert len(doc["nodes"]) == 2
    assert len(doc["links"]) == 1
    assert doc["links"][0]["relation"] == "references"
    assert doc["links"][0]["confidence"] == "EXTRACTED"


def test_export_writes_graph_json(tmp_path):
    out = tmp_path / "graph.json"
    path = export_to_graphify(_seed_store(), out)
    data = json.loads(path.read_text())
    assert data["nodes"]
    assert data["links"]
