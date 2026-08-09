"""In-memory vector store used for tests and local fallback.

This is NOT a production index; it provides the same ``VectorStore`` contract for
deterministic, dependency-free tests.
"""

from __future__ import annotations

import asyncio
import math
from typing import Any

from .vector import VectorResult, VectorStore, VectorStoreError


class InMemoryVectorStore:
    def __init__(self) -> None:
        self._items: dict[str, tuple[list[float], str, dict[str, Any]]] = {}
        self._lock = asyncio.Lock()

    async def health(self) -> bool:
        return True

    async def upsert(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict[str, Any]],
    ) -> None:
        if not (len(ids) == len(embeddings) == len(documents) == len(metadatas)):
            raise VectorStoreError("upsert arguments must have equal lengths")
        async with self._lock:
            for i, _id in enumerate(ids):
                self._items[_id] = (embeddings[i], documents[i], metadatas[i])

    async def query(
        self,
        query_embedding: list[float],
        *,
        top_k: int,
        where: dict[str, Any] | None = None,
    ) -> list[VectorResult]:
        async with self._lock:
            scored: list[tuple[float, str, str, dict[str, Any]]] = []
            for _id, (embedding, document, metadata) in self._items.items():
                if where and not _matches(metadata, where):
                    continue
                score = _cosine(query_embedding, embedding)
                scored.append((score, _id, document, metadata))
            scored.sort(key=lambda item: item[0], reverse=True)
            results: list[VectorResult] = []
            for score, _id, document, metadata in scored[: max(0, top_k)]:
                results.append(
                    VectorResult(id=_id, document=document, metadata=dict(metadata), distance=1.0 - score)
                )
            return results

    async def delete(self, ids: list[str]) -> None:
        async with self._lock:
            for _id in ids:
                self._items.pop(_id, None)

    async def count(self) -> int:
        async with self._lock:
            return len(self._items)


def _matches(metadata: dict[str, Any], where: dict[str, Any]) -> bool:
    for key, expected in where.items():
        actual = metadata.get(key)
        if isinstance(expected, dict):
            if "$eq" in expected and actual != expected["$eq"]:
                return False
            if "$ne" in expected and actual == expected["$ne"]:
                return False
            continue
        if actual != expected:
            return False
    return True


def _cosine(a: list[float], b: list[float]) -> float:
    if len(a) != len(b) or not a:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)
