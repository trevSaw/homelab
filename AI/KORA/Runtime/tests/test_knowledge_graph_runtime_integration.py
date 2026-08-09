"""Runtime integration tests for Phase 14.4 graph-aware Knowledge retrieval.

Hermetic: replaces the module-level KNOWLEDGE_SERVICE with a fake so no live
Chroma/Graphify is contacted.
"""

from __future__ import annotations

import unittest
from unittest import mock

from fastapi.testclient import TestClient

from app import main as main_module
from app.main import app


class FakeGraphKnowledgeService:
    def __init__(self, *, degraded: bool = False) -> None:
        self._degraded = degraded
        self.calls = 0

    async def build_graph_context(self, query: str):
        self.calls += 1
        if self._degraded:
            raise RuntimeError("graph down")
        return type(
            "Ctx",
            (),
            {
                "text": "[Knowledge: doc-1]\nmemory service details\n\n[Graph relationships]\nA --references--> B",
                "status": "ok",
                "knowledge_sources": ("doc-1",),
                "graph_entities": ({"entity_id": "e1", "canonical_name": "A"},),
                "graph_relationships": (
                    {"source_entity": "A", "relationship_type": "references", "target_entity": "B"},
                ),
            },
        )()

    async def build_context(self, query: str):
        return type(
            "Ctx",
            (),
            {"knowledge_text": "memory service details", "status": "ok", "sources": ("doc-1",), "chunks": ()},
        )()


class RuntimeGraphIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._original = main_module.KNOWLEDGE_SERVICE

    def tearDown(self) -> None:
        main_module.KNOWLEDGE_SERVICE = self._original

    def test_architecture_chat_uses_graph_context(self) -> None:
        fake = FakeGraphKnowledgeService()
        main_module.KNOWLEDGE_SERVICE = fake
        with mock.patch.object(main_module.httpx, "AsyncClient") as async_client_cls:
            async def respond(*args, **kwargs):
                return main_module.httpx.Response(
                    200, json={"message": {"content": "answer grounded in graph"}}
                )

            async_client_cls.return_value.post = mock.AsyncMock(side_effect=respond)
            async_client_cls.return_value.aclose = mock.AsyncMock(return_value=None)

            client = TestClient(app)
            response = client.post(
                "/v1/chat/completions",
                json={
                    "model": "test-model",
                    "messages": [{"role": "user", "content": "what does the architecture say about memory"}],
                },
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(fake.calls, 1)
        body = response.json()
        self.assertIn("graphify", body["kora"]["stores_queried"])
        self.assertIn("knowledge", body["kora"]["stores_queried"])

    def test_preference_chat_skips_graph(self) -> None:
        fake = FakeGraphKnowledgeService()
        main_module.KNOWLEDGE_SERVICE = fake
        with mock.patch.object(main_module.httpx, "AsyncClient") as async_client_cls:
            async def respond(*args, **kwargs):
                return main_module.httpx.Response(200, json={"message": {"content": "ok"}})

            async_client_cls.return_value.post = mock.AsyncMock(side_effect=respond)
            async_client_cls.return_value.aclose = mock.AsyncMock(return_value=None)

            client = TestClient(app)
            response = client.post(
                "/v1/chat/completions",
                json={
                    "model": "test-model",
                    "messages": [{"role": "user", "content": "i prefer concise"}],
                },
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(fake.calls, 0)
        body = response.json()
        self.assertIn("graphify", body["kora"]["stores_skipped"])

    def test_graph_backend_failure_does_not_break_chat(self) -> None:
        fake = FakeGraphKnowledgeService(degraded=True)
        main_module.KNOWLEDGE_SERVICE = fake
        with mock.patch.object(main_module.httpx, "AsyncClient") as async_client_cls:
            async def respond(*args, **kwargs):
                return main_module.httpx.Response(200, json={"message": {"content": "ok"}})

            async_client_cls.return_value.post = mock.AsyncMock(side_effect=respond)
            async_client_cls.return_value.aclose = mock.AsyncMock(return_value=None)

            client = TestClient(app)
            response = client.post(
                "/v1/chat/completions",
                json={
                    "model": "test-model",
                    "messages": [{"role": "user", "content": "what does the architecture say"}],
                },
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(fake.calls, 1)


if __name__ == "__main__":
    unittest.main()
