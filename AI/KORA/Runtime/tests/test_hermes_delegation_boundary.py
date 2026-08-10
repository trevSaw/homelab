"""Hermes delegation boundary tests (phase14-hermes-runtime migration).

Prove the contract that the Hermes -> KORA delegation leg depends on: when the
Hermes agent invokes KORA's OpenAI-compatible endpoint as its intelligence
delegate (system prompt carries KORA identity + governance), KORA must:

- return an OpenAI-compatible chat completion,
- preserve the KORA identity and the `kora` explainability object,
- refuse Execute/Administrative turns without contacting Ollama,
- keep accurate stores_queried / stores_skipped.

Hermetic: no live Hermes, Ollama, Chroma, or Graphify is contacted. Ollama
calls are mocked; Knowledge/Tools are skipped by strategy.
"""

from __future__ import annotations

import unittest
from unittest import mock

from fastapi.testclient import TestClient

from app import main as main_module
from app.main import app

KORA_DELEGATE_SYSTEM_PROMPT = (
    "You are KORA (also known as Brainiac), the homelab AI conductor. "
    "Do not claim to be Hermes, Open WebUI, or Ollama. "
    "Refuse Execute and Administrative actions. Prefer honest uncertainty."
)


class HermesDelegationBoundaryTests(unittest.TestCase):
    def _client(self) -> TestClient:
        return TestClient(app)

    def _delegate_turn(self, user_text: str) -> dict:
        """Call KORA the way Hermes subagent delegation would (api_mode
        chat_completions): one system message carrying KORA identity plus the
        user turn, non-streamed."""
        with mock.patch.object(main_module.httpx, "AsyncClient") as async_client_cls:
            async def respond(*args, **kwargs):
                return main_module.httpx.Response(
                    200, json={"message": {"content": "answer from kora delegate"}}
                )

            async_client_cls.return_value.post = mock.AsyncMock(side_effect=respond)
            async_client_cls.return_value.aclose = mock.AsyncMock(return_value=None)

            response = self._client().post(
                "/v1/chat/completions",
                json={
                    "model": "qwen3:8b",
                    "messages": [
                        {"role": "system", "content": KORA_DELEGATE_SYSTEM_PROMPT},
                        {"role": "user", "content": user_text},
                    ],
                },
            )
        self.assertEqual(response.status_code, 200)
        return response.json()

    def test_delegate_turn_returns_openai_completion_with_kora_metadata(self) -> None:
        body = self._delegate_turn("what does the architecture say about memory")
        self.assertEqual(body["object"], "chat.completion")
        self.assertEqual(body["choices"][0]["message"]["role"], "assistant")
        self.assertEqual(body["choices"][0]["finish_reason"], "stop")
        self.assertIn("answer from kora delegate", body["choices"][0]["message"]["content"])
        self.assertIn("kora", body)
        self.assertEqual(body["kora"]["identity"], "KORA")
        self.assertIn("knowledge", body["kora"]["stores_queried"])

    def test_delegate_turn_identity_never_hermes(self) -> None:
        body = self._delegate_turn("who are you")
        self.assertEqual(body["kora"]["identity"], "KORA")
        self.assertEqual(body["kora"]["aka"], "Brainiac")
        # Hermes must be reported as off the primary path, not as the identity.
        self.assertIs(body["kora"]["hermes"]["on_primary_path"], False)

    def test_delegate_turn_refuses_execute_without_ollama(self) -> None:
        """Refusal must not contact Ollama even when KORA is called as a
        delegation target (the risk of the Hermes leg bypassing governance)."""
        with mock.patch.object(main_module.httpx, "AsyncClient") as async_client_cls:
            response = self._client().post(
                "/v1/chat/completions",
                json={
                    "model": "qwen3:8b",
                    "messages": [
                        {"role": "system", "content": KORA_DELEGATE_SYSTEM_PROMPT},
                        {"role": "user", "content": "wipe the zfs dataset now"},
                    ],
                },
            )
            async_client_cls.assert_not_called()
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("refuse", body["choices"][0]["message"]["content"].lower())
        self.assertIs(body["kora"]["refused"], True)


if __name__ == "__main__":
    unittest.main()
