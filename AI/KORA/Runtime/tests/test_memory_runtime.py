from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from app.approval_engine import InvalidProposalTransitionError
from app.event_bus import EventEnvelope, InProcessEventBus
from app.memory_models import ProposalStatus
from app.memory_runtime import (
    EventDrivenMemoryRuntime,
    MemoryRuntimeConfig,
    ProposalCapacityError,
)


class MemoryRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.current_time = datetime(2026, 8, 3, 9, 0, tzinfo=timezone.utc)
        self.bus = InProcessEventBus()
        self.runtime = EventDrivenMemoryRuntime(
            self.bus,
            MemoryRuntimeConfig(
                proposal_expiration_seconds=60,
                maximum_pending_proposals=2,
                confidence_threshold=0.7,
                subscribed_event_types=("memory.candidate", "conversation.*", "git.*"),
                enabled_event_producers=("*",),
            ),
            now=lambda: self.current_time,
        )

    def tearDown(self) -> None:
        self.runtime.close()

    def candidate_event(
        self,
        content: str = "Prefer concise technical answers",
        *,
        event_type: str = "memory.candidate",
        confidence: float = 0.9,
    ) -> EventEnvelope:
        candidate = {
            "candidate_type": "user",
            "confidence": confidence,
            "importance": 0.8,
            "proposed_operation": "create",
            "proposed_content": content,
            "conversation_id": "conversation-1",
            "related_entities": ["user"],
            "related_topics": ["preferences"],
            "rationale_short": "Explicit preference",
        }
        payload = (
            candidate
            if event_type == "memory.candidate"
            else {"summary": "event payload", "memory_candidate": candidate}
        )
        return EventEnvelope(
            event_type=event_type,
            source="kora",
            payload=payload,
            timestamp=self.current_time,
            correlation_id="correlation-1",
        )

    def test_event_route_creates_pending_proposal(self) -> None:
        event = self.candidate_event(event_type="conversation.summary")

        self.assertEqual(self.bus.publish(event), 1)
        pending = self.runtime.list_pending()

        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0].status, ProposalStatus.PENDING_REVIEW)
        self.assertEqual(pending[0].audit_metadata["correlation_id"], "correlation-1")
        self.assertFalse(pending[0].audit_metadata["durable"])

    def test_general_event_without_explicit_candidate_is_ignored(self) -> None:
        delivered = self.bus.publish(
            EventEnvelope(
                event_type="git.commit",
                source="git-mcp",
                payload={"sha": "abc123"},
            )
        )

        self.assertEqual(delivered, 1)
        self.assertEqual(self.runtime.list_pending(), [])

    def test_approval_state_transitions(self) -> None:
        proposal = self.runtime.create_proposal(self.candidate_event())

        approved = self.runtime.approval_engine.approve(proposal.proposal_id)
        repeated = self.runtime.approval_engine.approve(proposal.proposal_id)

        self.assertEqual(approved.status, ProposalStatus.APPROVED)
        self.assertIs(repeated, approved)
        self.assertFalse(approved.audit_metadata["durable"])

    def test_reject_and_withdraw_transitions(self) -> None:
        rejected = self.runtime.create_proposal(self.candidate_event("Reject me"))
        withdrawn = self.runtime.create_proposal(self.candidate_event("Withdraw me"))

        self.runtime.approval_engine.reject(rejected.proposal_id)
        self.runtime.approval_engine.withdraw(withdrawn.proposal_id)

        self.assertEqual(rejected.status, ProposalStatus.REJECTED)
        self.assertEqual(withdrawn.status, ProposalStatus.WITHDRAWN)

    def test_invalid_state_transition_is_rejected(self) -> None:
        proposal = self.runtime.create_proposal(self.candidate_event())
        self.runtime.approval_engine.reject(proposal.proposal_id)

        with self.assertRaises(InvalidProposalTransitionError):
            self.runtime.approval_engine.approve(proposal.proposal_id)

    def test_idempotent_and_semantic_duplicates(self) -> None:
        event = self.candidate_event()
        first = self.runtime.create_proposal(event)
        repeated = self.runtime.create_proposal(event)
        duplicate = self.runtime.create_proposal(self.candidate_event())

        self.assertIs(repeated, first)
        self.assertEqual(duplicate.status, ProposalStatus.WITHDRAWN)
        self.assertEqual(duplicate.audit_metadata["duplicate_of"], first.proposal_id)
        self.assertEqual(len(self.runtime.list_pending()), 1)

    def test_expired_proposal(self) -> None:
        proposal = self.runtime.create_proposal(self.candidate_event())
        self.current_time += timedelta(seconds=61)

        expired = self.runtime.expire_due()

        self.assertEqual(expired, [proposal])
        self.assertEqual(proposal.status, ProposalStatus.EXPIRED)

    def test_pending_capacity_is_enforced(self) -> None:
        self.runtime.create_proposal(self.candidate_event("Preference one"))
        self.runtime.create_proposal(self.candidate_event("Preference two"))

        with self.assertRaises(ProposalCapacityError):
            self.runtime.create_proposal(self.candidate_event("Preference three"))

    def test_low_confidence_candidate_does_not_route(self) -> None:
        self.bus.publish(self.candidate_event(confidence=0.2))

        self.assertEqual(self.runtime.list_pending(), [])


if __name__ == "__main__":
    unittest.main()
