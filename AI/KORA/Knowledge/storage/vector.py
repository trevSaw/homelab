"""Vector store abstraction.

KORA depends on this abstraction, not directly on Chroma. Chroma is
infrastructure/indexing; it is never the Knowledge authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class VectorStoreError(RuntimeError):
    pass


class VectorStoreUnavailableError(VectorStoreError):
    pass


@dataclass(frozen=True, slots=True)
class VectorResult:
    id: str
    document: str
    metadata: dict[str, Any]
    distance: float


class VectorStore(Protocol):
    async def health(self) -> bool: ...

    async def upsert(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict[str, Any]],
    ) -> None: ...

    async def query(
        self,
        query_embedding: list[float],
        *,
        top_k: int,
        where: dict[str, Any] | None = None,
    ) -> list[VectorResult]: ...

    async def delete(self, ids: list[str]) -> None: ...

    async def count(self) -> int: ...
