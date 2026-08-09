"""Tests for the vector store abstraction, in-memory store, and Chroma adapter."""

import asyncio
import json

import httpx

from ..storage.chroma import ChromaVectorStore
from ..storage.in_memory_vector import InMemoryVectorStore
from ..storage.vector import VectorStoreError, VectorStoreUnavailableError


def test_in_memory_upsert_query_and_delete():
    store = InMemoryVectorStore()
    asyncio.run(
        store.upsert(
            ["a:1:0", "a:1:1"],
            [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
            ["kora is a conductor", "memory is separate"],
            [{"document_id": "a", "document_version": "1"}, {"document_id": "a", "document_version": "1"}],
        )
    )
    assert asyncio.run(store.count()) == 2
    results = asyncio.run(store.query([1.0, 0.0, 0.0], top_k=2))
    assert results[0].id == "a:1:0"
    assert results[0].metadata["document_id"] == "a"
    asyncio.run(store.delete(["a:1:0"]))
    assert asyncio.run(store.count()) == 1


def test_in_memory_metadata_filtering():
    store = InMemoryVectorStore()
    asyncio.run(
        store.upsert(
            ["a:1:0", "b:1:0"],
            [[1.0, 0.0], [1.0, 0.0]],
            ["doc a", "doc b"],
            [{"document_id": "a"}, {"document_id": "b"}],
        )
    )
    results = asyncio.run(
        store.query([1.0, 0.0], top_k=5, where={"document_id": "b"})
    )
    assert [r.id for r in results] == ["b:1:0"]


def test_in_memory_idempotent_upsert_overwrites():
    store = InMemoryVectorStore()
    asyncio.run(
        store.upsert(["a:1:0"], [[1.0, 0.0]], ["old"], [{"document_id": "a"}])
    )
    asyncio.run(
        store.upsert(["a:1:0"], [[0.0, 1.0]], ["new"], [{"document_id": "a"}])
    )
    assert asyncio.run(store.count()) == 1
    results = asyncio.run(store.query([0.0, 1.0], top_k=1))
    assert results[0].document == "new"


def test_in_memory_unequal_lengths_rejected():
    store = InMemoryVectorStore()
    try:
        asyncio.run(store.upsert(["a"], [[1.0]], ["doc"], []))
        assert False, "expected VectorStoreError"
    except VectorStoreError:
        pass


class _ChromaHandler(httpx.MockTransport):
    def __init__(self, *, health_fail: bool = False) -> None:
        super().__init__(handler=self._handler)
        self._health_fail = health_fail
        self.collection_id = "col-1"
        self.upserts = []
        self.queries = []
        self.deletes = []

    def _handler(self, request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        if url.endswith("/api/v2/heartbeat"):
            if self._health_fail:
                return httpx.Response(503)
            return httpx.Response(200, json={"nanosecond heartbeat": 1})
        if url.endswith("/collections"):
            return httpx.Response(200, json={"id": self.collection_id, "name": "kora"})
        if url.endswith("/upsert"):
            self.upserts.append(json.loads(request.content))
            return httpx.Response(200, json={})
        if url.endswith("/query"):
            self.queries.append(json.loads(request.content))
            return httpx.Response(
                200,
                json={
                    "ids": [["a:1:0"]],
                    "documents": [["kora is a conductor"]],
                    "metadatas": [[{"document_id": "a", "document_version": "1"}]],
                    "distances": [[0.1]],
                },
            )
        if url.endswith("/delete"):
            self.deletes.append(json.loads(request.content))
            return httpx.Response(200, json={"deleted": 1})
        if url.endswith("/count"):
            return httpx.Response(200, json=1)
        return httpx.Response(404, json={"error": "not found"})


def _chroma_store(handler: _ChromaHandler) -> ChromaVectorStore:
    return ChromaVectorStore(
        base_url="http://chromadb:8000",
        collection="kora_knowledge",
        transport=handler,
    )


def test_chroma_health():
    handler = _ChromaHandler()
    store = _chroma_store(handler)
    assert asyncio.run(store.health()) is True


def test_chroma_health_unavailable():
    handler = _ChromaHandler(health_fail=True)
    store = _chroma_store(handler)
    assert asyncio.run(store.health()) is False


def test_chroma_upsert_and_query():
    handler = _ChromaHandler()
    store = _chroma_store(handler)
    asyncio.run(
        store.upsert(
            ["a:1:0"],
            [[1.0, 0.0]],
            ["kora is a conductor"],
            [{"document_id": "a", "document_version": "1"}],
        )
    )
    assert handler.upserts[0]["ids"] == ["a:1:0"]
    results = asyncio.run(store.query([1.0, 0.0], top_k=2))
    assert results[0].id == "a:1:0"
    assert results[0].metadata["document_id"] == "a"
    assert results[0].distance == 0.1


def test_chroma_delete():
    handler = _ChromaHandler()
    store = _chroma_store(handler)
    asyncio.run(store.delete(["a:1:0"]))
    assert handler.deletes[0]["ids"] == ["a:1:0"]


def test_chroma_unavailable_raises():
    class DownHandler(httpx.MockTransport):
        def __init__(self) -> None:
            super().__init__(handler=self._handler)

        def _handler(self, request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("chroma down")

    store = _chroma_store(DownHandler())
    try:
        asyncio.run(store.upsert(["a"], [[1.0]], ["d"], [{}]))
        assert False, "expected VectorStoreUnavailableError"
    except VectorStoreUnavailableError:
        pass


def test_chroma_unequal_lengths_rejected():
    store = _chroma_store(_ChromaHandler())
    try:
        asyncio.run(store.upsert(["a"], [[1.0]], ["doc"], []))
        assert False, "expected VectorStoreError"
    except VectorStoreError:
        pass
