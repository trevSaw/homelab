"""Approval-to-persistence workflow coordination.

The Commit Coordinator is not a policy authority. It only executes persistence
workflow after Approval Engine has completed the authorization decision.
"""

from __future__ import annotations

import asyncio
import hashlib

from .durable_memory import DurableMemory, DurableMemoryError, DurableMemoryStore
from .memory_models import MemoryProposal, PersistenceStatus, ProposalStatus
from .memory_runtime import EventDrivenMemoryRuntime


class CommitFailedError(RuntimeError):
    pass


class CommitContentUnavailableError(CommitFailedError):
    pass


class MemoryCommitCoordinator:
    def __init__(
        self,
        memory_runtime: EventDrivenMemoryRuntime,
        durable_store: DurableMemoryStore,
    ) -> None:
        self._runtime = memory_runtime
        self._durable_store = durable_store
        self._lock = asyncio.Lock()

    async def approve_and_commit(
        self,
        proposal_id: str,
        *,
        actor: str,
        text_final: str | None = None,
    ) -> MemoryProposal:
        async with self._lock:
            proposal = self._runtime.get_proposal(proposal_id)
            if proposal.persistence_status == PersistenceStatus.COMMITTED:
                return proposal
            if text_final is not None:
                if proposal.status != ProposalStatus.PENDING_REVIEW:
                    raise CommitFailedError("approved content cannot be edited after authorization")
                proposal.proposed_content = self._runtime.validate_final_content(text_final)
                self._runtime.save_proposal(proposal)

            content = proposal.proposed_content
            if not content:
                existing = await self._durable_store.find_by_proposal_id(proposal_id)
                if existing:
                    return self._finalize(proposal, existing, actor="recovery")
                proposal.persistence_status = PersistenceStatus.COMMIT_FAILED
                self._runtime.save_proposal(proposal)
                raise CommitContentUnavailableError(
                    "approved content is unavailable; create a new proposal"
                )

            if proposal.status == ProposalStatus.PENDING_REVIEW:
                self._runtime.repository.record_event(
                    proposal_id,
                    "approval_intent",
                    actor,
                    {"explicit": True},
                )
                self._runtime.approval_engine.approve(proposal_id, actor=actor)
            elif proposal.status != ProposalStatus.APPROVED:
                raise CommitFailedError(
                    f"proposal in {proposal.status.value} cannot be committed"
                )

            proposal.persistence_status = PersistenceStatus.APPROVED_PENDING_COMMIT
            self._runtime.save_proposal(proposal)
            self._runtime.repository.record_event(
                proposal_id,
                "approval_authorized",
                actor,
                {"persistence_status": proposal.persistence_status.value},
            )

            try:
                durable = await self._durable_store.commit(proposal, content)
            except DurableMemoryError as exc:
                proposal.persistence_status = PersistenceStatus.COMMIT_FAILED
                self._runtime.save_proposal(proposal)
                self._runtime.repository.record_event(
                    proposal_id,
                    "commit_failed",
                    "commit-coordinator",
                    {"error_type": type(exc).__name__},
                )
                raise CommitFailedError("approved Memory commit failed") from exc
            return self._finalize(proposal, durable, actor="commit-coordinator")

    async def recover(self) -> dict[str, int]:
        result = {"committed": 0, "pending": 0, "failed": 0}
        for proposal in self._runtime.list_all():
            if proposal.status == ProposalStatus.PENDING_REVIEW:
                intents = [
                    item
                    for item in self._runtime.repository.audit_history(proposal.proposal_id)
                    if item["event_type"] == "approval_intent"
                ]
                if not intents:
                    result["pending"] += 1
                    continue
                actor = str(intents[-1]["actor"])
                try:
                    await self.approve_and_commit(proposal.proposal_id, actor=actor)
                    result["committed"] += 1
                except CommitFailedError:
                    result["failed"] += 1
                continue

            if proposal.status == ProposalStatus.APPROVED and proposal.persistence_status in {
                PersistenceStatus.APPROVED_PENDING_COMMIT,
                PersistenceStatus.COMMIT_FAILED,
            }:
                existing = await self._durable_store.find_by_proposal_id(
                    proposal.proposal_id
                )
                if existing:
                    self._finalize(proposal, existing, actor="recovery")
                    result["committed"] += 1
                else:
                    proposal.persistence_status = PersistenceStatus.COMMIT_FAILED
                    self._runtime.save_proposal(proposal)
                    result["failed"] += 1
        return result

    def _finalize(
        self,
        proposal: MemoryProposal,
        durable: DurableMemory,
        *,
        actor: str,
    ) -> MemoryProposal:
        proposal.persistence_status = PersistenceStatus.COMMITTED
        proposal.durable_memory_id = durable.memory_id
        proposal.content_hash = hashlib.sha256(durable.content.encode()).hexdigest()
        self._runtime.save_proposal(proposal)
        self._runtime.repository.record_event(
            proposal.proposal_id,
            "commit_succeeded",
            actor,
            {"durable_memory_id": durable.memory_id, "content_hash": proposal.content_hash},
        )
        proposal.proposed_content = None
        return proposal
