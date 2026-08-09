"""Runtime integration tests for Phase 14.3 Knowledge retrieval in the chat path.

These tests are hermetic: they replace the module-level KNOWLEDGE_SERVICE with a
fake so no live Chroma/Ollama is contacted.
"""

from __future__ import annotations

import unittest
from unittest import mock

from fastapi.testclient import TestClient

from app import main as main_module
from app.main import app


class FakeKnowledgeService:
    def __init__(self, *, degraded: bool = False) -> None:
        self._degraded = degraded
        self.calls = 0

    async def build_context(self, query: str):
        self.calls += 1
        if self._degraded:
            raise RuntimeError("chroma down")
        return type(
            "Ctx",
            (),
            {
                "knowledge_text": "[Source: doc-1 v1]\nkora is a conductor",
                "status": "ok",
                "sources": ("doc-1",),
                "chunks": ({"chunk_id": "c1"},),
            },
        )()

    async def health(self):
        return {"status": "ok", "phase": "14.3", "indexed_documents": 1}


class RuntimeKnowledgeIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._original = main_module.KNOWLEDGE_SERVICE

    def tearDown(self) -> None:
        main_module.KNOWLEDGE_SERVICE = self._original

    def test_architecture_chat_retrieves_knowledge_and_reaches_llm(self) -> None:
        fake = FakeKnowledgeService()
        main_module.KNOWLEDGE_SERVICE = fake
        with mock.patch.object(main_module.httpx, "AsyncClient") as async_client_cls:
            async def respond(*args, **kwargs):
                return main_module.httpx.Response(
                    200, json={"message": {"content": "answer grounded in knowledge"}}
                )

            async_client_cls.return_value.post = mock.AsyncMock(side_effect=respond)
            async_client_cls.return_value.aclose = mock.AsyncMock(return_value=None)

            client = TestClient(app)
            response = client.post(
                "/v1/chat/completions",
                json={
                    "model": "test-model",
                    "messages": [{"role": "user", "content": "what does the architecture say about kora"}],
                },
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(fake.calls, 1)
        body = response.json()
        self.assertIn("answer grounded in knowledge", body["choices"][0]["message"]["content"])
        self.assertIn("knowledge", body["kora"]["stores_queried"])

    def test_preference_chat_does_not_retrieve_knowledge(self) -> None:
        fake = FakeKnowledgeService()
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
                    "messages": [{"role": "user", "content": "i always prefer concise answers"}],
                },
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(fake.calls, 0)

    def test_knowledge_backend_failure_does_not_break_chat(self) -> None:
        fake = FakeKnowledgeService(degraded=True)
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
