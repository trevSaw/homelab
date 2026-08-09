"""Phase 14.2D production-readiness tests for health endpoint and graceful
degradation.

These tests validate existing behavior only. No production functionality is
added to satisfy them.
"""

from __future__ import annotations

import unittest
from unittest import mock

from fastapi.testclient import TestClient

from app import main as main_module
from app.main import app


class HealthEndpointTests(unittest.TestCase):
    client = TestClient(app)

    def test_health_returns_expected_shape(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        for key in (
            "status",
            "product",
            "profile",
            "phase",
            "ollama",
            "council_mode",
            "hermes_role",
            "event_bus",
            "pending_memory_proposals",
            "memory_repository",
            "memory_recovery",
        ):
            self.assertIn(key, payload)
        self.assertEqual(payload["product"], "KORA")
        self.assertIn(payload["status"], {"ok", "degraded"})

    def test_health_degrades_when_ollama_unreachable(self) -> None:
        with mock.patch.object(main_module.httpx, "AsyncClient") as async_client_cls:
            async def raise_connect(*args, **kwargs):
                raise main_module.httpx.ConnectError("down")

            async_client_cls.return_value.__aenter__ = mock.AsyncMock(
                side_effect=raise_connect
            )
            async_client_cls.return_value.__aexit__ = mock.AsyncMock(return_value=None)

            response = self.client.get("/health")
            self.assertEqual(response.status_code, 200)
            payload = response.json()
            self.assertEqual(payload["status"], "degraded")
            self.assertIs(payload["ollama"], False)

    def test_root_endpoint_reports_identity(self) -> None:
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["product"], "KORA")
        self.assertEqual(payload["phase"], "14.3")


if __name__ == "__main__":
    unittest.main()
