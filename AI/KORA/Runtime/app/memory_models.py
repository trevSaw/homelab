"""Proposal and persistence-state models for the KORA Memory Runtime."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ProposalStatus(str, Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    WITHDRAWN = "withdrawn"


class ProposedOperation(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class PersistenceStatus(str, Enum):
    NOT_REQUESTED = "not_requested"
    APPROVED_PENDING_COMMIT = "approved_pending_commit"
    COMMITTED = "committed"
    COMMIT_FAILED = "commit_failed"


@dataclass(slots=True)
class MemoryProposal:
    proposal_id: str
    source: str
    timestamp: datetime
    conversation_id: str | None
    candidate_type: str
    confidence: float
    importance: float
    proposed_operation: ProposedOperation
    proposed_content: str | None
    related_entities: list[str]
    related_topics: list[str]
    status: ProposalStatus
    created_at: datetime
    expires_at: datetime
    audit_metadata: dict[str, Any]
    persistence_status: PersistenceStatus = PersistenceStatus.NOT_REQUESTED
    durable_memory_id: str | None = None
    content_hash: str | None = None
    schema_version: str = "1.0"

    def __post_init__(self) -> None:
        self.timestamp = _as_utc(self.timestamp)
        self.created_at = _as_utc(self.created_at)
        self.expires_at = _as_utc(self.expires_at)
        if not self.proposal_id:
            raise ValueError("proposal_id is required")
        if not self.source:
            raise ValueError("source is required")
        if not self.candidate_type:
            raise ValueError("candidate_type is required")
        if self.status in {ProposalStatus.DRAFT, ProposalStatus.PENDING_REVIEW} and (
            not self.proposed_content or not self.proposed_content.strip()
        ):
            raise ValueError("proposed_content is required")
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")
        if not 0 <= self.importance <= 1:
            raise ValueError("importance must be between 0 and 1")
        if self.expires_at <= self.created_at:
            raise ValueError("expires_at must be after created_at")

    @classmethod
    def new(
        cls,
        *,
        source: str,
        timestamp: datetime,
        conversation_id: str | None,
        candidate_type: str,
        confidence: float,
        importance: float,
        proposed_operation: ProposedOperation,
        proposed_content: str,
        related_entities: list[str],
        related_topics: list[str],
        created_at: datetime,
        expires_at: datetime,
        audit_metadata: dict[str, Any],
    ) -> "MemoryProposal":
        return cls(
            proposal_id=str(uuid.uuid4()),
            source=source,
            timestamp=timestamp,
            conversation_id=conversation_id,
            candidate_type=candidate_type,
            confidence=confidence,
            importance=importance,
            proposed_operation=proposed_operation,
            proposed_content=proposed_content,
            related_entities=related_entities,
            related_topics=related_topics,
            status=ProposalStatus.DRAFT,
            created_at=created_at,
            expires_at=expires_at,
            audit_metadata=audit_metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "conversation_id": self.conversation_id,
            "candidate_type": self.candidate_type,
            "confidence": self.confidence,
            "importance": self.importance,
            "proposed_operation": self.proposed_operation.value,
            "proposed_content": self.proposed_content,
            "related_entities": list(self.related_entities),
            "related_topics": list(self.related_topics),
            "status": self.status.value,
            "persistence_status": self.persistence_status.value,
            "durable_memory_id": self.durable_memory_id,
            "content_hash": self.content_hash,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "audit_metadata": self.audit_metadata,
            "schema_version": self.schema_version,
        }


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
