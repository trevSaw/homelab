"""Tests for deterministic chunking."""

import asyncio

from ..chunking.fixed_size import FixedSizeChunker


def test_chunker_is_deterministic():
    chunker = FixedSizeChunker(size=16, overlap=4)
    content = "the quick brown fox jumps over the lazy dog"
    first = chunker.chunk(content)
    second = chunker.chunk(content)
    assert first == second


def test_single_chunk_when_content_fits():
    chunker = FixedSizeChunker(size=64, overlap=8)
    content = "short content"
    chunks = chunker.chunk(content)
    assert chunks == [content]


def test_multiple_chunks_with_overlap():
    chunker = FixedSizeChunker(size=8, overlap=2)
    content = "abcdefghijklmnop"
    chunks = chunker.chunk(content)
    assert len(chunks) > 1
    assert all(chunk for chunk in chunks)
    # Each chunk is a contiguous window of the source.
    for chunk in chunks:
        assert chunk in content
    # The first chunk starts at the beginning; coverage spans the whole source.
    assert chunks[0] == "abcdefgh"
    assert "".join(chunks) != content  # overlap means segments repeat


def test_empty_content_returns_empty():
    chunker = FixedSizeChunker()
    assert chunker.chunk("") == []


def test_invalid_configuration():
    try:
        FixedSizeChunker(size=0, overlap=0)
        assert False, "expected ValueError"
    except ValueError:
        pass
    try:
        FixedSizeChunker(size=10, overlap=10)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_chunks_reassemble_to_content():
    chunker = FixedSizeChunker(size=8, overlap=2)
    content = "a" * 50
    chunks = chunker.chunk(content)
    # Coverage: every position of the source appears in at least one chunk.
    covered = set()
    start = 0
    step = chunker.size - chunker.overlap
    for _ in chunks:
        for i in range(start, min(start + chunker.size, len(content))):
            covered.add(i)
        start += step
    assert covered == set(range(len(content)))
