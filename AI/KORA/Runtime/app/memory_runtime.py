"""Event-driven Memory proposal runtime."""

from __future__ import annotations

import hashlib
import json
import logging
import re
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable, Protocol

from .approval_engine import InMemoryApprovalEngine, ProposalNotFoundError
from .event_bus import EventBus, EventEnvelope
from .memory_models import (
    MemoryProposal,
    ProposedOperation,
    ProposalStatus,
    utc_now,
)
from .proposal_repository import InMemoryProposalRepository, ProposalRepository

log = logging.getLogger("kora.memory_runtime")

_SECRET_PATTERN = re.compile(
    r"(password\s*[:=]|api[_ -]?key\s*[:=]|private[_ -]?key|bearer\s+[a-z0-9._-]+)",
    re.IGNORECASE,
)


class ProposalIneligibleError(ValueError):
    pass


class ProposalCapacityError(RuntimeError):
    pass


class MemoryRuntime(Protocol):
    def create_proposal(self, event: EventEnvelope) -> MemoryProposal: ...

    def list_pending(self) -> list[MemoryProposal]: ...

    def get_proposal(self, proposal_id: str) -> MemoryProposal: ...


@dataclass(frozen=True, slots=True)
class MemoryRuntimeConfig:
    proposal_expiration_seconds: int = 604800
    maximum_pending_proposals: int = 100
    confidence_threshold: float = 0.7
    proposal_categories: tuple[str, ...] = ("user", "project", "operational", "temporary")
    subscribed_event_types: tuple[str, ...] = (
        "memory.candidate",
        "conversation.*",
        "filesystem.*",
        "git.*",
        "calendar.*",
        "email.*",
        "docker.*",
        "graph.*",
    )
    enabled_event_producers: tuple[str, ...] = ("kora",)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "MemoryRuntimeConfig":
        proposals = value.get("proposals") or {}
        events = value.get("events") or {}
        return cls(
            proposal_expiration_seconds=int(proposals.get("expiration_seconds", 604800)),
            maximum_pending_proposals=int(proposals.get("maximum_pending", 100)),
            confidence_threshold=float(proposals.get("confidence_threshold", 0.7)),
            proposal_categories=tuple(
                proposals.get("categories") or ("user", "project", "operational", "temporary")
            ),
            subscribed_event_types=tuple(
                events.get("memory_runtime_subscriptions")
                or (
                    "memory.candidate",
                    "conversation.*",
                    "filesystem.*",
                    "git.*",
                    "calendar.*",
                    "email.*",
                    "docker.*",
                    "graph.*",
                )
            ),
            enabled_event_producers=tuple(events.get("enabled_producers") or ("kora",)),
        )

    def __post_init__(self) -> None:
        if self.proposal_expiration_seconds <= 0:
            raise ValueError("proposal_expiration_seconds must be positive")
        if self.maximum_pending_proposals <= 0:
            raise ValueError("maximum_pending_proposals must be positive")
        if not 0 <= self.confidence_threshold <= 1:
            raise ValueError("confidence_threshold must be between 0 and 1")


class EventDrivenMemoryRuntime:
    """Consumes general events and manages proposal lifecycle in volatile memory."""

    def __init__(
        self,
        event_bus: EventBus,
        config: MemoryRuntimeConfig | None = None,
        *,
        now: Callable[[], datetime] = utc_now,
        repository: ProposalRepository | None = None,
    ) -> None:
        self._event_bus = event_bus
        self._config = config or MemoryRuntimeConfig()
        self._now = now
        self.repository = repository or InMemoryProposalRepository()
        self._proposals: dict[str, MemoryProposal] = {
            proposal.proposal_id: proposal for proposal in self.repository.load_all()
        }
        self._event_index: dict[str, str] = {}
        self._fingerprint_index: dict[str, str] = {}
        for proposal in self._proposals.values():
            source_event = proposal.audit_metadata.get("source_event") or {}
            if source_event.get("event_id"):
                self._event_index[str(source_event["event_id"])] = proposal.proposal_id
            fingerprint = proposal.audit_metadata.get("fingerprint")
            if fingerprint and proposal.status in {
                ProposalStatus.DRAFT,
                ProposalStatus.PENDING_REVIEW,
                ProposalStatus.APPROVED,
            }:
                self._fingerprint_index[str(fingerprint)] = proposal.proposal_id
        self._lock = threading.RLock()
        self.approval_engine = InMemoryApprovalEngine(self._proposals)
        self._subscriptions = [
            self._event_bus.subscribe(topic, self._receive_event, self._source_enabled)
            for topic in self._config.subscribed_event_types
        ]

    def close(self) -> None:
        for subscription in self._subscriptions:
            self._event_bus.unsubscribe(subscription)
        self._subscriptions.clear()

    def create_proposal(self, event: EventEnvelope) -> MemoryProposal:
        with self._lock:
            existing_id = self._event_index.get(event.event_id)
            if existing_id:
                return self._proposals[existing_id]

            candidate = self._candidate_from_event(event)
            self._validate_eligibility(event, candidate)
            fingerprint = self._fingerprint(event, candidate)
            duplicate_id = self._fingerprint_index.get(fingerprint)

            self.expire_due(now=self._now())
            if duplicate_id is None and len(self.list_pending()) >= self._config.maximum_pending_proposals:
                raise ProposalCapacityError("maximum pending proposals reached")

            proposal = self._build_proposal(event, candidate, fingerprint)
            self._proposals[proposal.proposal_id] = proposal
            self._event_index[event.event_id] = proposal.proposal_id
            self.repository.save(proposal)
            self.approval_engine.submit(proposal.proposal_id)

            if duplicate_id is not None:
                proposal.audit_metadata["duplicate_of"] = duplicate_id
                self.approval_engine.withdraw(
                    proposal.proposal_id,
                    actor="memory-runtime",
                    reason=f"semantic duplicate of {duplicate_id}",
                )
                proposal.proposed_content = None
            else:
                self._fingerprint_index[fingerprint] = proposal.proposal_id
            self.repository.save(proposal)
            self.repository.record_event(
                proposal.proposal_id,
                "proposal_created",
                "memory-runtime",
                {"status": proposal.status.value, "correlation_id": event.correlation_id},
            )
            return proposal

    def list_pending(self) -> list[MemoryProposal]:
        return self.list_by_status(ProposalStatus.PENDING_REVIEW)

    def list_by_status(self, status: ProposalStatus) -> list[MemoryProposal]:
        return sorted(
            (proposal for proposal in self._proposals.values() if proposal.status == status),
            key=lambda proposal: proposal.created_at,
        )

    def list_all(self) -> list[MemoryProposal]:
        return sorted(self._proposals.values(), key=lambda proposal: proposal.created_at)

    def get_proposal(self, proposal_id: str) -> MemoryProposal:
        try:
            return self._proposals[proposal_id]
        except KeyError as exc:
            raise ProposalNotFoundError(proposal_id) from exc

    def save_proposal(self, proposal: MemoryProposal) -> None:
        self.repository.save(proposal)

    def reject(self, proposal_id: str, *, actor: str, reason: str | None = None) -> MemoryProposal:
        proposal = self.approval_engine.reject(proposal_id, actor=actor, reason=reason)
        self.repository.save(proposal)
        self.repository.record_event(proposal_id, "proposal_rejected", actor, {"reason": reason})
        proposal.proposed_content = None
        return proposal

    def withdraw(
        self,
        proposal_id: str,
        *,
        actor: str,
        reason: str | None = None,
    ) -> MemoryProposal:
        proposal = self.approval_engine.withdraw(proposal_id, actor=actor, reason=reason)
        self.repository.save(proposal)
        self.repository.record_event(proposal_id, "proposal_withdrawn", actor, {"reason": reason})
        proposal.proposed_content = None
        return proposal

    def expire(self, proposal_id: str, *, actor: str) -> MemoryProposal:
        proposal = self.approval_engine.expire(proposal_id, actor=actor)
        self.repository.save(proposal)
        self.repository.record_event(
            proposal_id,
            "proposal_expired",
            actor,
            {"expires_at": proposal.expires_at.isoformat()},
        )
        proposal.proposed_content = None
        return proposal

    def validate_final_content(self, content: str) -> str:
        normalized = content.strip()
        if not normalized:
            raise ProposalIneligibleError("approved content is required")
        if _SECRET_PATTERN.search(normalized):
            raise ProposalIneligibleError("approved content may contain a secret")
        return normalized

    def expire_due(self, *, now: datetime | None = None) -> list[MemoryProposal]:
        current = now or self._now()
        expired: list[MemoryProposal] = []
        for proposal in tuple(self._proposals.values()):
            if proposal.status == ProposalStatus.PENDING_REVIEW and proposal.expires_at <= current:
                item = self.approval_engine.expire(proposal.proposal_id, now=current)
                self.repository.save(item)
                self.repository.record_event(
                    item.proposal_id,
                    "proposal_expired",
                    "approval-engine",
                    {"expires_at": item.expires_at.isoformat()},
                )
                item.proposed_content = None
                expired.append(item)
        return expired

    def _receive_event(self, event: EventEnvelope) -> None:
        try:
            self.create_proposal(event)
        except ProposalIneligibleError:
            log.debug(
                "event not eligible event_type=%s event_id=%s correlation_id=%s",
                event.event_type,
                event.event_id,
                event.correlation_id,
            )
        except ProposalCapacityError:
            log.warning(
                "proposal capacity reached event_id=%s correlation_id=%s",
                event.event_id,
                event.correlation_id,
            )

    def _source_enabled(self, event: EventEnvelope) -> bool:
        enabled = self._config.enabled_event_producers
        return "*" in enabled or event.source in enabled

    def _candidate_from_event(self, event: EventEnvelope) -> dict[str, Any]:
        candidate = (
            event.payload
            if event.event_type == "memory.candidate"
            else event.payload.get("memory_candidate")
        )
        if not isinstance(candidate, dict):
            raise ProposalIneligibleError("event does not contain an explicit memory candidate")
        return candidate

    def _validate_eligibility(self, event: EventEnvelope, candidate: dict[str, Any]) -> None:
        if not self._source_enabled(event):
            raise ProposalIneligibleError(f"event source {event.source!r} is disabled")
        category = str(candidate.get("candidate_type") or candidate.get("category") or "")
        if category not in self._config.proposal_categories:
            raise ProposalIneligibleError(f"candidate type {category!r} is not enabled")
        confidence = _number(candidate.get("confidence"), "confidence")
        if confidence < self._config.confidence_threshold:
            raise ProposalIneligibleError("candidate confidence is below threshold")
        content = str(candidate.get("proposed_content") or candidate.get("text") or "").strip()
        if not content:
            raise ProposalIneligibleError("candidate content is required")
        if _SECRET_PATTERN.search(content):
            raise ProposalIneligibleError("candidate content may contain a secret")

    def _build_proposal(
        self,
        event: EventEnvelope,
        candidate: dict[str, Any],
        fingerprint: str,
    ) -> MemoryProposal:
        created_at = self._now()
        category = str(candidate.get("candidate_type") or candidate.get("category"))
        operation = ProposedOperation(str(candidate.get("proposed_operation", "create")))
        content = str(candidate.get("proposed_content") or candidate.get("text")).strip()
        return MemoryProposal.new(
            source=event.source,
            timestamp=event.timestamp,
            conversation_id=_optional_string(
                candidate.get("conversation_id") or event.metadata.get("conversation_id")
            ),
            candidate_type=category,
            confidence=_number(candidate.get("confidence"), "confidence"),
            importance=_number(candidate.get("importance", 0.5), "importance"),
            proposed_operation=operation,
            proposed_content=content,
            related_entities=_string_list(candidate.get("related_entities")),
            related_topics=_string_list(candidate.get("related_topics")),
            created_at=created_at,
            expires_at=created_at
            + timedelta(seconds=self._config.proposal_expiration_seconds),
            audit_metadata={
                "proposed_by": "kora",
                "source_event": event.to_dict(),
                "correlation_id": event.correlation_id,
                "rationale_short": str(candidate.get("rationale_short") or ""),
                "fingerprint": fingerprint,
                "durable": False,
                "transitions": [],
            },
        )

    @staticmethod
    def _fingerprint(event: EventEnvelope, candidate: dict[str, Any]) -> str:
        normalized = {
            "source": event.source,
            "conversation_id": candidate.get("conversation_id")
            or event.metadata.get("conversation_id"),
            "candidate_type": candidate.get("candidate_type") or candidate.get("category"),
            "operation": candidate.get("proposed_operation", "create"),
            "content": " ".join(
                str(candidate.get("proposed_content") or candidate.get("text") or "")
                .lower()
                .split()
            ),
        }
        serialized = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialized.encode()).hexdigest()


def _number(value: Any, field_name: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ProposalIneligibleError(f"{field_name} must be numeric") from exc
    if not 0 <= number <= 1:
        raise ProposalIneligibleError(f"{field_name} must be between 0 and 1")
    return number


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ProposalIneligibleError("related values must be lists of strings")
    return value


def _optional_string(value: Any) -> str | None:
    return None if value is None else str(value)
