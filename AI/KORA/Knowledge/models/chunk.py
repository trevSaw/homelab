"""Knowledge chunk model.

A ``KnowledgeChunk`` is a deterministic, ordered segment of a knowledge version.
Every chunk retains enough metadata to reconstruct its provenance: document
identity, document version, chunk index, content hash, and (when indexed) the
embedding model used.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


def chunk_id(document_id: str, version: str, index: int) -> str:
    return f"{document_id}:{version}:{index}"


@dataclass(frozen=True, slots=True)
class KnowledgeChunk:
    document_id: str
    version: str
    content_hash: str
    source: str
    index: int
    content: str
    embedding_model: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def chunk_id(self) -> str:
        return chunk_id(self.document_id, self.version, self.index)

    def to_metadata(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "document_version": self.version,
            "content_hash": self.content_hash,
            "source": self.source,
            "chunk_index": self.index,
            "embedding_model": self.embedding_model or "",
        }

    def to_dict(self) -> dict[str, Any]:
        data = self.to_metadata()
        data["content"] = self.content
        return data
