from __future__ import annotations

import sqlite3
import tempfile
import unittest
from datetime import datetime, timezone

from app.commit_coordinator import CommitFailedError, MemoryCommitCoordinator
from app.durable_memory import DurableMemory, DurableMemoryError
from app.event_bus import EventEnvelope, InProcessEventBus
from app.memory_models import PersistenceStatus, ProposalStatus
from app.memory_runtime import EventDrivenMemoryRuntime, MemoryRuntimeConfig
from app.proposal_repository import SQLiteProposalRepository


class FakeDurableStore:
    def __init__(self) -> None:
        self.memories: dict[str, DurableMemory] = {}
        self.commit_calls = 0
        self.fail = False

    async def health(self) -> bool:
        return True

    async def commit(self, proposal, content: str) -> DurableMemory:
        self.commit_calls += 1
        if self.fail:
            raise DurableMemoryError("backend failed")
        existing = self.memories.get(proposal.proposal_id)
        if existing:
            return existing
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

    async def find_by_proposal_id(self, proposal_id: str):
        return self.memories.get(proposal_id)

    async def list_memories(self, *, category=None, limit=100):
        values = list(self.memories.values())
        if category:
            values = [item for item in values if item.category == category]
        return values[:limit]


class DurableMemoryTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.database_path = f"{self.temp.name}/memory.sqlite3"
        self.repository = SQLiteProposalRepository(self.database_path)
        self.bus = InProcessEventBus()
        self.runtime = EventDrivenMemoryRuntime(
            self.bus,
            MemoryRuntimeConfig(enabled_event_producers=("*",)),
            repository=self.repository,
        )
        self.store = FakeDurableStore()
        self.coordinator = MemoryCommitCoordinator(self.runtime, self.store)

    def tearDown(self) -> None:
        self.runtime.close()
        self.repository.close()
        self.temp.cleanup()

    def create_proposal(self, content: str = "Use concise answers"):
        return self.runtime.create_proposal(
            EventEnvelope(
                event_type="memory.candidate",
                source="kora",
                payload={
                    "candidate_type": "user",
                    "confidence": 0.95,
                    "importance": 0.8,
                    "proposed_content": content,
                },
            )
        )

    async def test_only_approved_proposal_is_persisted_and_redacted(self) -> None:
        proposal = self.create_proposal()

        result = await self.coordinator.approve_and_commit(
            proposal.proposal_id,
            actor="memory-user",
        )

        self.assertEqual(result.status, ProposalStatus.APPROVED)
        self.assertEqual(result.persistence_status, PersistenceStatus.COMMITTED)
        self.assertEqual(self.store.commit_calls, 1)
        self.assertIsNone(result.proposed_content)
        with sqlite3.connect(self.database_path) as connection:
            stored = connection.execute(
                "SELECT proposed_content FROM proposals WHERE proposal_id = ?",
                (proposal.proposal_id,),
            ).fetchone()[0]
        self.assertIsNone(stored)

    async def test_duplicate_approval_is_idempotent(self) -> None:
        proposal = self.create_proposal()
        first = await self.coordinator.approve_and_commit(
            proposal.proposal_id,
            actor="memory-user",
        )
        second = await self.coordinator.approve_and_commit(
            proposal.proposal_id,
            actor="memory-user",
        )

        self.assertIs(first, second)
        self.assertEqual(self.store.commit_calls, 1)

    async def test_commit_failure_separates_approval_and_persistence_state(self) -> None:
        proposal = self.create_proposal()
        self.store.fail = True

        with self.assertRaises(CommitFailedError):
            await self.coordinator.approve_and_commit(
                proposal.proposal_id,
                actor="memory-user",
            )

        self.assertEqual(proposal.status, ProposalStatus.APPROVED)
        self.assertEqual(proposal.persistence_status, PersistenceStatus.COMMIT_FAILED)
        with sqlite3.connect(self.database_path) as connection:
            stored = connection.execute(
                "SELECT proposed_content FROM proposals WHERE proposal_id = ?",
                (proposal.proposal_id,),
            ).fetchone()[0]
        self.assertIsNone(stored)

    async def test_nonapproved_terminal_states_never_persist(self) -> None:
        rejected = self.create_proposal("Reject this")
        withdrawn = self.create_proposal("Withdraw this")
        expired = self.create_proposal("Expire this")

        self.runtime.reject(rejected.proposal_id, actor="memory-user")
        self.runtime.withdraw(withdrawn.proposal_id, actor="memory-operator")
        expired.expires_at = datetime(2000, 1, 1, tzinfo=timezone.utc)
        self.runtime.expire(expired.proposal_id, actor="memory-operator")

        self.assertEqual(self.store.commit_calls, 0)
        self.assertEqual(rejected.status, ProposalStatus.REJECTED)
        self.assertEqual(withdrawn.status, ProposalStatus.WITHDRAWN)
        self.assertEqual(expired.status, ProposalStatus.EXPIRED)

    async def test_restart_recovers_explicit_approval_intent(self) -> None:
        proposal = self.create_proposal("Recover after restart")
        self.repository.record_event(
            proposal.proposal_id,
            "approval_intent",
            "memory-user",
            {"explicit": True},
        )
        self.runtime.close()
        self.repository.close()

        self.repository = SQLiteProposalRepository(self.database_path)
        self.bus = InProcessEventBus()
        self.runtime = EventDrivenMemoryRuntime(
            self.bus,
            MemoryRuntimeConfig(enabled_event_producers=("*",)),
            repository=self.repository,
        )
        self.coordinator = MemoryCommitCoordinator(self.runtime, self.store)

        result = await self.coordinator.recover()
        recovered = self.runtime.get_proposal(proposal.proposal_id)

        self.assertEqual(result["committed"], 1)
        self.assertEqual(recovered.status, ProposalStatus.APPROVED)
        self.assertEqual(recovered.persistence_status, PersistenceStatus.COMMITTED)

    async def test_pending_proposal_restores_without_approval(self) -> None:
        proposal = self.create_proposal("Still pending")
        self.runtime.close()
        self.repository.close()

        self.repository = SQLiteProposalRepository(self.database_path)
        self.bus = InProcessEventBus()
        self.runtime = EventDrivenMemoryRuntime(
            self.bus,
            MemoryRuntimeConfig(enabled_event_producers=("*",)),
            repository=self.repository,
        )
        self.coordinator = MemoryCommitCoordinator(self.runtime, self.store)
        result = await self.coordinator.recover()

        self.assertEqual(result["pending"], 1)
        self.assertEqual(
            self.runtime.get_proposal(proposal.proposal_id).status,
            ProposalStatus.PENDING_REVIEW,
        )
        self.assertEqual(self.store.commit_calls, 0)


if __name__ == "__main__":
    unittest.main()
