"""In‑memory KnowledgeStore implementation used for tests.

The store holds :class:`KnowledgeDocument` objects in a dict keyed by ``doc_id``.
"""

from __future__ import annotations

import asyncio
from typing import Dict, List

from ..models.document import KnowledgeDocument
from .interface import KnowledgeStore


class InMemoryKnowledgeStore(KnowledgeStore):
    def __init__(self) -> None:
        self._store: Dict[str, KnowledgeDocument] = {}
        self._lock = asyncio.Lock()

    async def save(self, doc: KnowledgeDocument) -> None:
        async with self._lock:
            self._store[doc.doc_id] = doc

    async def list_documents(self, *, limit: int = 100) -> List[KnowledgeDocument]:
        async with self._lock:
            return list(self._store.values())[:limit]

    async def find_by_id(self, doc_id: str) -> KnowledgeDocument | None:
        async with self._lock:
            return self._store.get(doc_id)
