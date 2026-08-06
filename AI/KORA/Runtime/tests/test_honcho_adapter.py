from __future__ import annotations

import json
import unittest
from datetime import datetime, timedelta, timezone

import httpx

from app.honcho_adapter import HonchoAdapter, HonchoAdapterConfig
from app.memory_models import MemoryProposal, ProposalStatus, ProposedOperation


def proposal() -> MemoryProposal:
    now = datetime.now(timezone.utc)
    return MemoryProposal(
        proposal_id="proposal-1",
        source="kora",
        timestamp=now,
        conversation_id="conversation-1",
        candidate_type="user",
        confidence=0.9,
        importance=0.8,
        proposed_operation=ProposedOperation.CREATE,
        proposed_content="Prefer concise answers",
        related_entities=["user"],
        related_topics=["preferences"],
        status=ProposalStatus.APPROVED,
        created_at=now,
        expires_at=now + timedelta(days=1),
        audit_metadata={},
    )


class HonchoAdapterTests(unittest.IsolatedAsyncioTestCase):
    async def test_direct_conclusion_commit_and_idempotent_lookup(self) -> None:
        conclusions: list[dict] = []
        create_calls = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal create_calls
            if request.url.path.endswith("/conclusions/list"):
                return httpx.Response(200, json={"items": conclusions})
            if request.url.path.endswith("/conclusions"):
                create_calls += 1
                body = json.loads(request.content)
                item = {
                    "id": "conclusion-1",
                    "content": body["conclusions"][0]["content"],
                    "observer_id": "kora",
                    "observed_id": "user",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
                conclusions.append(item)
                return httpx.Response(200, json=[item])
            return httpx.Response(404)

        adapter = HonchoAdapter(
            HonchoAdapterConfig(
                base_url="http://memory-backend",
                workspace_id="kora",
                observer_id="kora",
                observed_id="user",
                retry_base_seconds=0,
            ),
            transport=httpx.MockTransport(handler),
        )
        try:
            first = await adapter.commit(proposal(), "Prefer concise answers")
            second = await adapter.commit(proposal(), "Prefer concise answers")
            listed = await adapter.list_memories(category="user")
        finally:
            await adapter.close()

        self.assertEqual(first.memory_id, "conclusion-1")
        self.assertEqual(second.memory_id, first.memory_id)
        self.assertEqual(create_calls, 1)
        self.assertEqual(listed[0].source_class, "memory")
        self.assertEqual(listed[0].content, "Prefer concise answers")

    async def test_transient_health_failure_retries(self) -> None:
        attempts = 0

        def handler(_: httpx.Request) -> httpx.Response:
            nonlocal attempts
            attempts += 1
            return httpx.Response(500 if attempts == 1 else 200, json={"status": "ok"})

        adapter = HonchoAdapter(
            HonchoAdapterConfig(
                base_url="http://memory-backend",
                workspace_id="kora",
                observer_id="kora",
                observed_id="user",
                retry_attempts=2,
                retry_base_seconds=0,
            ),
            transport=httpx.MockTransport(handler),
        )
        try:
            self.assertTrue(await adapter.health())
        finally:
            await adapter.close()
        self.assertEqual(attempts, 2)


if __name__ == "__main__":
    unittest.main()
