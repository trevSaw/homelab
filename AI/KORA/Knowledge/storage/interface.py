"""Knowledge storage abstraction.

Implementations provide async CRUD operations for :class:`KnowledgeDocument`.
"""

from __future__ import annotations

from typing import List

from ..models.document import KnowledgeDocument


class KnowledgeStore:
    """Protocol‑like base for knowledge storage backends.

    The interface mirrors the ``DurableMemoryStore`` pattern – all methods are
    ``async`` to keep the runtime consistent.
    """

    async def save(self, doc: KnowledgeDocument) -> None:
        raise NotImplementedError

    async def list_documents(self, *, limit: int = 100) -> List[KnowledgeDocument]:
        raise NotImplementedError

    async def find_by_id(self, doc_id: str) -> KnowledgeDocument | None:
        raise NotImplementedError
