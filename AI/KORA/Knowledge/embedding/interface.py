"""Embedding provider abstraction.

KORA depends on this abstraction, not on a specific embedding implementation.
The active provider is configuration-driven. Multiple providers may be
introduced later without changing the rest of the Knowledge architecture.
"""

from __future__ import annotations

from typing import Protocol


class EmbeddingError(RuntimeError):
    pass


class EmbeddingProvider(Protocol):
    @property
    def model_id(self) -> str: ...

    async def embed(self, texts: list[str]) -> list[list[float]]: ...
