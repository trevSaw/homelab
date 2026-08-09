"""Knowledge version model.

A ``KnowledgeVersion`` is a specific, immutable version of a knowledge document.
It carries stable document identity, version identity, a deterministic content
hash, the source, and the normalized content for this version.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping

from .document import KnowledgeDocument


def sha256_hex(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def document_id_from_source(source: str) -> str:
    """Stable knowledge identity derived from the source reference."""
    return sha256_hex(source)


@dataclass(frozen=True, slots=True)
class KnowledgeVersion:
    document_id: str
    version: str
    content_hash: str
    source: str
    content: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def from_document(
        cls,
        document: KnowledgeDocument,
        *,
        document_id: str | None = None,
        version: str | None = None,
        created_at: datetime | None = None,
    ) -> "KnowledgeVersion":
        content_hash = document.doc_id  # KnowledgeDocument.doc_id is the SHA-256 of content
        return cls(
            document_id=document_id or document_id_from_source(document.source),
            version=version or content_hash[:16],
            content_hash=content_hash,
            source=document.source,
            content=document.content,
            metadata=dict(document.metadata),
            created_at=created_at or datetime.now(timezone.utc),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "document_id": self.document_id,
            "version": self.version,
            "content_hash": self.content_hash,
            "source": self.source,
            "content": self.content,
            "metadata": dict(self.metadata),
            "created_at": self.created_at.isoformat(),
        }
