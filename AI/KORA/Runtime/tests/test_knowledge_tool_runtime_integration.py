"""Runtime integration tests for Phase 14.5 Tool Platform in the chat path.

Hermetic: replaces module-level TOOL_PLATFORM and KNOWLEDGE_SERVICE with fakes.
"""

from __future__ import annotations

import unittest
from unittest import mock

from fastapi.testclient import TestClient

from app import main as main_module
from app.main import app


class FakeToolPlatform:
    def __init__(self, tools=None):
        self._tools = tools or [
            type("T", (), {
                "tool_id": "ollama.list_models",
                "name": "ollama.list_models",
                "risk": "read_only",
                "requires_approval": False,
                "result": {"models": ["qwen3:8b"]},
            })()
        ]
        self.invocations = []

    def list_tools(self, *, enabled_only=False):
        return self._tools

    async def invoke(self, tool_id, arguments):
        self.invocations.append(tool_id)
        return type("R", (), {
            "success": True,
            "result": {"models": ["qwen3:8b"]},
            "error": None,
        })()


class FakeKnowledge:
    def __init__(self):
        self.graph_assembler = None

    async def build_context(self, q):
        return type("C", (), {"knowledge_text": "", "status": "ok", "sources": (), "chunks": ()})()


class RuntimeToolIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._orig_tools = main_module.TOOL_PLATFORM
        self._orig_knowledge = main_module.KNOWLEDGE_SERVICE
        main_module.KNOWLEDGE_SERVICE = FakeKnowledge()

    def tearDown(self) -> None:
        main_module.TOOL_PLATFORM = self._orig_tools
        main_module.KNOWLEDGE_SERVICE = self._orig_knowledge

    def _client(self):
        return TestClient(app)

    def test_operational_query_invokes_read_only_tool(self) -> None:
        tools = FakeToolPlatform()
        main_module.TOOL_PLATFORM = tools
        with mock.patch.object(main_module.httpx, "AsyncClient") as async_client_cls:
            async def respond(*args, **kwargs):
                return main_module.httpx.Response(
                    200, json={"message": {"content": "models: qwen3:8b"}}
                )

            async_client_cls.return_value.post = mock.AsyncMock(side_effect=respond)
            async_client_cls.return_value.aclose = mock.AsyncMock(return_value=None)

            response = self._client().post(
                "/v1/chat/completions",
                json={"model": "m", "messages": [{"role": "user", "content": "list the running models"}]},
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tools.invocations, ["ollama.list_models"])
        body = response.json()
        self.assertIn("tools", body["kora"]["stores_queried"])

    def test_architecture_query_does_not_invoke_tools(self) -> None:
        tools = FakeToolPlatform()
        main_module.TOOL_PLATFORM = tools
        with mock.patch.object(main_module.httpx, "AsyncClient") as async_client_cls:
            async def respond(*args, **kwargs):
                return main_module.httpx.Response(200, json={"message": {"content": "ok"}})

            async_client_cls.return_value.post = mock.AsyncMock(side_effect=respond)
            async_client_cls.return_value.aclose = mock.AsyncMock(return_value=None)

            response = self._client().post(
                "/v1/chat/completions",
                json={"model": "m", "messages": [{"role": "user", "content": "what does the architecture say about memory"}]},
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tools.invocations, [])
        body = response.json()
        self.assertIn("tools", body["kora"]["stores_skipped"])

    def test_tool_invocation_failure_does_not_break_chat(self) -> None:
        class FailingTools(FakeToolPlatform):
            async def invoke(self, tool_id, arguments):
                self.invocations.append(tool_id)
                return type("R", (), {"success": False, "result": None, "error": "down"})()

        tools = FailingTools()
        main_module.TOOL_PLATFORM = tools
        with mock.patch.object(main_module.httpx, "AsyncClient") as async_client_cls:
            async def respond(*args, **kwargs):
                return main_module.httpx.Response(200, json={"message": {"content": "ok"}})

            async_client_cls.return_value.post = mock.AsyncMock(side_effect=respond)
            async_client_cls.return_value.aclose = mock.AsyncMock(return_value=None)

            response = self._client().post(
                "/v1/chat/completions",
                json={"model": "m", "messages": [{"role": "user", "content": "what models are running"}]},
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tools.invocations, ["ollama.list_models"])


if __name__ == "__main__":
    unittest.main()
