"""Phase 14.2D production-readiness tests for graceful degradation and chat
path store isolation.

These tests validate existing behavior only. No production functionality is
added to satisfy them.
"""

from __future__ import annotations

import unittest
from unittest import mock

from fastapi.testclient import TestClient

from app import main as main_module
from app.main import app, classify, select_strategy


class GracefulDegradationTests(unittest.TestCase):
    def test_chat_returns_502_when_ollama_unreachable(self) -> None:
        with mock.patch.object(main_module.httpx, "AsyncClient") as async_client_cls:
            async def raise_connect(*args, **kwargs):
                raise main_module.httpx.ConnectError("ollama down")

            async_client_cls.return_value.post = mock.AsyncMock(
                side_effect=raise_connect
            )
            async_client_cls.return_value.aclose = mock.AsyncMock(return_value=None)

            client = TestClient(app)
            response = client.post(
                "/v1/chat/completions",
                json={"model": "test-model", "messages": [{"role": "user", "content": "hi"}]},
            )
            self.assertEqual(response.status_code, 502)

    def test_ollama_tags_falls_back_to_default_model_on_failure(self) -> None:
        with mock.patch.object(main_module.httpx, "AsyncClient") as async_client_cls:
            async def raise_connect(*args, **kwargs):
                raise main_module.httpx.ConnectError("ollama down")

            async_client_cls.return_value.__aenter__ = mock.AsyncMock(
                side_effect=raise_connect
            )
            async_client_cls.return_value.__aexit__ = mock.AsyncMock(return_value=None)

            import asyncio

            models = asyncio.run(main_module.ollama_tags())
            self.assertEqual(len(models), 1)
            self.assertEqual(models[0]["id"], main_module.DEFAULT_MODEL)


class ChatPathStoreIsolationTests(unittest.TestCase):
    def test_strategy_memory_and_tools_never_queried(self) -> None:
        # Phase 14.3: Knowledge retrieval is enabled for architecture-style
        # queries; Memory and Tools remain off the chat path.
        for label in ("general", "preference", "architecture", "identity"):
            strategy = select_strategy({"label": label, "confidence": "high", "rationale": "t"})
            self.assertIs(strategy["query_memory"], False)
            self.assertIs(strategy["query_tools"], False)
            self.assertIn("memory", strategy["stores_skipped"])
            self.assertIn("tools", strategy["stores_skipped"])

    def test_strategy_knowledge_queried_only_for_architecture(self) -> None:
        architecture = select_strategy({"label": "architecture", "confidence": "high", "rationale": "t"})
        preference = select_strategy({"label": "preference", "confidence": "high", "rationale": "t"})
        self.assertIs(architecture["query_knowledge"], True)
        self.assertIn("knowledge", architecture["stores_queried"])
        self.assertIs(preference["query_knowledge"], False)
        self.assertIn("knowledge", preference["stores_skipped"])
        self.assertEqual(preference["budgets"]["knowledge"], 0)

    def test_execute_and_admin_requests_are_refused(self) -> None:
        client = TestClient(app)
        execute_response = client.post(
            "/v1/chat/completions",
            json={
                "model": "test-model",
                "messages": [{"role": "user", "content": "delete the docker volume now"}],
            },
        )
        self.assertEqual(execute_response.status_code, 200)
        content = execute_response.json()["choices"][0]["message"]["content"]
        self.assertIn("refuse", content.lower())

    def test_classifier_labels_execute_and_admin_patterns(self) -> None:
        self.assertEqual(classify("wipe the zfs dataset")["label"], "execute_forbidden")
        self.assertEqual(
            classify("rotate the root password")["label"], "administrative_forbidden"
        )
        self.assertEqual(classify("what is your name")["label"], "identity")


if __name__ == "__main__":
    unittest.main()
