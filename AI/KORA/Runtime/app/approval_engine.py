"""Approval state-transition contract with an ephemeral Phase 14.2A adapter."""

from __future__ import annotations

from collections.abc import MutableMapping
from datetime import datetime
from typing import Protocol

from .memory_models import MemoryProposal, ProposalStatus, utc_now


class ProposalNotFoundError(KeyError):
    pass


class InvalidProposalTransitionError(ValueError):
    pass


class ApprovalEngine(Protocol):
    def approve(self, proposal_id: str, *, actor: str = "user") -> MemoryProposal: ...

    def reject(
        self,
        proposal_id: str,
        *,
        actor: str = "user",
        reason: str | None = None,
    ) -> MemoryProposal: ...

    def expire(
        self,
        proposal_id: str,
        *,
        now: datetime | None = None,
        actor: str = "approval-engine",
    ) -> MemoryProposal: ...

    def withdraw(
        self,
        proposal_id: str,
        *,
        actor: str = "kora",
        reason: str | None = None,
    ) -> MemoryProposal: ...


class InMemoryApprovalEngine:
    """Owns proposal transitions only; approval performs no durable write."""

    def __init__(self, proposals: MutableMapping[str, MemoryProposal]) -> None:
        self._proposals = proposals

    def submit(self, proposal_id: str) -> MemoryProposal:
        return self._transition(
            proposal_id,
            expected={ProposalStatus.DRAFT},
            target=ProposalStatus.PENDING_REVIEW,
            actor="memory-runtime",
            reason="eligible proposal submitted for review",
        )

    def approve(self, proposal_id: str, *, actor: str = "user") -> MemoryProposal:
        proposal = self._get(proposal_id)
        if proposal.status == ProposalStatus.APPROVED:
            return proposal
        return self._transition(
            proposal_id,
            expected={ProposalStatus.PENDING_REVIEW},
            target=ProposalStatus.APPROVED,
            actor=actor,
            reason="explicit approval",
        )

    def reject(
        self,
        proposal_id: str,
        *,
        actor: str = "user",
        reason: str | None = None,
    ) -> MemoryProposal:
        return self._transition(
            proposal_id,
            expected={ProposalStatus.PENDING_REVIEW},
            target=ProposalStatus.REJECTED,
            actor=actor,
            reason=reason or "explicit rejection",
        )

    def expire(
        self,
        proposal_id: str,
        *,
        now: datetime | None = None,
        actor: str = "approval-engine",
    ) -> MemoryProposal:
        proposal = self._get(proposal_id)
        transition_at = now or utc_now()
        if transition_at < proposal.expires_at:
            raise InvalidProposalTransitionError(
                f"proposal {proposal_id} cannot expire before {proposal.expires_at.isoformat()}"
            )
        return self._transition(
            proposal_id,
            expected={ProposalStatus.PENDING_REVIEW},
            target=ProposalStatus.EXPIRED,
            actor=actor,
            reason="proposal expiration reached",
            transition_at=transition_at,
        )

    def withdraw(
        self,
        proposal_id: str,
        *,
        actor: str = "kora",
        reason: str | None = None,
    ) -> MemoryProposal:
        return self._transition(
            proposal_id,
            expected={ProposalStatus.PENDING_REVIEW},
            target=ProposalStatus.WITHDRAWN,
            actor=actor,
            reason=reason or "proposal withdrawn",
        )

    def _get(self, proposal_id: str) -> MemoryProposal:
        try:
            return self._proposals[proposal_id]
        except KeyError as exc:
            raise ProposalNotFoundError(proposal_id) from exc

    def _transition(
        self,
        proposal_id: str,
        *,
        expected: set[ProposalStatus],
        target: ProposalStatus,
        actor: str,
        reason: str,
        transition_at: datetime | None = None,
    ) -> MemoryProposal:
        proposal = self._get(proposal_id)
        if proposal.status not in expected:
            raise InvalidProposalTransitionError(
                f"invalid transition {proposal.status.value} -> {target.value}"
            )
        previous = proposal.status
        proposal.status = target
        proposal.audit_metadata.setdefault("transitions", []).append(
            {
                "from": previous.value,
                "to": target.value,
                "actor": actor,
                "reason": reason,
                "timestamp": (transition_at or utc_now()).isoformat(),
            }
        )
        return proposal
