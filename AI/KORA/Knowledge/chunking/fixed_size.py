"""Deterministic fixed-size chunker.

A simple, deterministic character-window chunker with configurable overlap. The
output is a pure function of the input content and configuration, so repeated
chunking of identical content yields identical chunks.
"""

from __future__ import annotations

from .interface import Chunker


class FixedSizeChunker:
    def __init__(self, size: int = 512, overlap: int = 64) -> None:
        if size <= 0:
            raise ValueError("chunk size must be positive")
        if overlap < 0 or overlap >= size:
            raise ValueError("overlap must be non-negative and smaller than size")
        self._size = size
        self._overlap = overlap

    @property
    def size(self) -> int:
        return self._size

    @property
    def overlap(self) -> int:
        return self._overlap

    def chunk(self, content: str) -> list[str]:
        if not content:
            return []
        step = self._size - self._overlap
        chunks: list[str] = []
        start = 0
        end = 0
        n = len(content)
        while start < n:
            end = min(start + self._size, n)
            chunks.append(content[start:end])
            if end == n:
                break
            start += step
        return chunks
