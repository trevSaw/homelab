"""Provider-neutral durable Memory contracts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from .memory_models import MemoryProposal


class DurableMemoryError(RuntimeError):
    pass


class DurableMemoryUnavailableError(DurableMemoryError):
    pass


@dataclass(frozen=True, slots=True)
class DurableMemory:
    memory_id: str
    proposal_id: str
    content: str
    category: str
    source: str
    conversation_id: str | None
    confidence: float
    importance: float
    related_entities: tuple[str, ...]
    related_topics: tuple[str, ...]
    created_at: datetime
    source_class: str = "memory"

    def to_dict(self) -> dict[str, object]:
        return {
            "memory_id": self.memory_id,
            "proposal_id": self.proposal_id,
            "content": self.content,
            "category": self.category,
            "source": self.source,
            "conversation_id": self.conversation_id,
            "confidence": self.confidence,
            "importance": self.importance,
            "related_entities": list(self.related_entities),
            "related_topics": list(self.related_topics),
            "created_at": self.created_at.isoformat(),
            "source_class": self.source_class,
        }


class DurableMemoryStore(Protocol):
    async def health(self) -> bool: ...

    async def commit(self, proposal: MemoryProposal, content: str) -> DurableMemory: ...

    async def find_by_proposal_id(self, proposal_id: str) -> DurableMemory | None: ...

    async def list_memories(
        self,
        *,
        category: str | None = None,
        limit: int = 100,
    ) -> list[DurableMemory]: ...


class DisabledDurableMemoryStore:
    async def health(self) -> bool:
        return False

    async def commit(self, proposal: MemoryProposal, content: str) -> DurableMemory:
        raise DurableMemoryUnavailableError("durable Memory is not configured")

    async def find_by_proposal_id(self, proposal_id: str) -> DurableMemory | None:
        return None

    async def list_memories(
        self,
        *,
        category: str | None = None,
        limit: int = 100,
    ) -> list[DurableMemory]:
        raise DurableMemoryUnavailableError("durable Memory is not configured")
