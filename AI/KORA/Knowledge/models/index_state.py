"""Index metadata / synchronization state model.

``IndexMetadata`` records the state of a knowledge document's vector index so the
system can reason about whether authoritative Knowledge and its vector index are
synchronized. It is persisted outside Chroma and is never authoritative Knowledge.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


class IndexState:
    INDEXED = "indexed"
    FAILED = "failed"
    RETIRED = "retired"


@dataclass(frozen=True, slots=True)
class IndexMetadata:
    document_id: str
    version: str
    content_hash: str
    index_state: str
    embedding_model: str
    source: str
    chunk_ids: tuple[str, ...] = field(default_factory=tuple)
    chunk_count: int = 0
    indexed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "document_id": self.document_id,
            "version": self.version,
            "content_hash": self.content_hash,
            "index_state": self.index_state,
            "embedding_model": self.embedding_model,
            "source": self.source,
            "chunk_ids": list(self.chunk_ids),
            "chunk_count": self.chunk_count,
            "indexed_at": self.indexed_at.isoformat(),
            "last_error": self.last_error,
        }
