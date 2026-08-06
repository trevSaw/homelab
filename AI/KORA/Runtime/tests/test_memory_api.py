from __future__ import annotations

import unittest
import uuid
from datetime import datetime, timezone

from fastapi.testclient import TestClient

import app.main as main_module
from app.auth import BearerAuthorizer, MemoryScope
from app.commit_coordinator import MemoryCommitCoordinator
from app.durable_memory import DurableMemory
from app.event_bus import EventEnvelope
from app.main import EVENT_BUS, MEMORY_RUNTIME, app


class ApiDurableStore:
    def __init__(self) -> None:
        self.memories = {}

    async def health(self):
        return True

    async def commit(self, proposal, content):
        memory = self.memories.get(proposal.proposal_id)
        if memory is None:
            memory = DurableMemory(
                memory_id=f"memory-{proposal.proposal_id}",
                proposal_id=proposal.proposal_id,
                content=content,
                category=proposal.candidate_type,
                source=proposal.source,
                conversation_id=proposal.conversation_id,
                confidence=proposal.confidence,
                importance=proposal.importance,
                related_entities=tuple(proposal.related_entities),
                related_topics=tuple(proposal.related_topics),
                created_at=datetime.now(timezone.utc),
            )
            self.memories[proposal.proposal_id] = memory
        return memory

    async def find_by_proposal_id(self, proposal_id):
        return self.memories.get(proposal_id)

    async def list_memories(self, *, category=None, limit=100):
        return list(self.memories.values())[:limit]


class MemoryApiTests(unittest.TestCase):
    client = TestClient(app)

    @classmethod
    def setUpClass(cls) -> None:
        main_module.MEMORY_AUTHORIZER = BearerAuthorizer(
            {
                "reader": ("read-token", frozenset({MemoryScope.READ})),
                "user": (
                    "approval-token",
                    frozenset({MemoryScope.READ, MemoryScope.APPROVE}),
                ),
                "operator": (
                    "operator-token",
                    frozenset({MemoryScope.READ, MemoryScope.OPERATE}),
                ),
            }
        )
        cls.store = ApiDurableStore()
        main_module.COMMIT_COORDINATOR = MemoryCommitCoordinator(MEMORY_RUNTIME, cls.store)

    def create_proposal(self) -> str:
        unique = uuid.uuid4().hex
        event = EventEnvelope(
            event_type="memory.candidate",
            source="kora",
            correlation_id=f"correlation-{unique}",
            payload={
                "candidate_type": "project",
                "confidence": 0.95,
                "importance": 0.8,
                "proposed_operation": "create",
                "proposed_content": f"Phase 14.2A API test {unique}",
                "conversation_id": f"conversation-{unique}",
            },
        )
        self.assertEqual(EVENT_BUS.publish(event), 1)
        proposal = next(
            item
            for item in MEMORY_RUNTIME.list_pending()
            if item.audit_metadata["correlation_id"] == event.correlation_id
        )
        return proposal.proposal_id

    def test_read_only_list_and_get(self) -> None:
        proposal_id = self.create_proposal()

        headers = {"Authorization": "Bearer read-token"}
        listed = self.client.get(
            "/v1/memory/proposals?status=pending_review",
            headers=headers,
        )
        fetched = self.client.get(
            f"/v1/memory/proposals/{proposal_id}",
            headers=headers,
        )

        self.assertEqual(listed.status_code, 200)
        self.assertIn(proposal_id, [item["proposal_id"] for item in listed.json()["data"]])
        self.assertEqual(fetched.status_code, 200)
        self.assertEqual(fetched.json()["proposal_id"], proposal_id)

    def test_api_validation_and_missing_proposal(self) -> None:
        headers = {"Authorization": "Bearer read-token"}
        invalid = self.client.get(
            "/v1/memory/proposals?status=not-a-state",
            headers=headers,
        )
        missing = self.client.get(
            "/v1/memory/proposals/does-not-exist",
            headers=headers,
        )

        self.assertEqual(invalid.status_code, 422)
        self.assertEqual(missing.status_code, 404)

    def test_memory_api_requires_authentication_and_scopes(self) -> None:
        proposal_id = self.create_proposal()
        unauthenticated = self.client.get("/v1/memory/proposals")
        unauthorized = self.client.post(
            f"/v1/memory/proposals/{proposal_id}/approve",
            headers={"Authorization": "Bearer operator-token"},
            json={},
        )

        self.assertEqual(unauthenticated.status_code, 401)
        self.assertEqual(unauthorized.status_code, 403)

    def test_authenticated_reject_mutation(self) -> None:
        proposal_id = self.create_proposal()
        response = self.client.post(
            f"/v1/memory/proposals/{proposal_id}/reject",
            headers={"Authorization": "Bearer approval-token"},
            json={"reason": "not durable"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "rejected")

    def test_authenticated_approve_persists(self) -> None:
        proposal_id = self.create_proposal()
        response = self.client.post(
            f"/v1/memory/proposals/{proposal_id}/approve",
            headers={"Authorization": "Bearer approval-token"},
            json={},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "approved")
        self.assertEqual(response.json()["persistence_status"], "committed")
        self.assertIn(proposal_id, self.store.memories)

    def test_operator_scope_controls_withdraw(self) -> None:
        proposal_id = self.create_proposal()
        user_response = self.client.post(
            f"/v1/memory/proposals/{proposal_id}/withdraw",
            headers={"Authorization": "Bearer approval-token"},
            json={},
        )
        operator_response = self.client.post(
            f"/v1/memory/proposals/{proposal_id}/withdraw",
            headers={"Authorization": "Bearer operator-token"},
            json={},
        )

        self.assertEqual(user_response.status_code, 403)
        self.assertEqual(operator_response.status_code, 200)
        self.assertEqual(operator_response.json()["status"], "withdrawn")


if __name__ == "__main__":
    unittest.main()
