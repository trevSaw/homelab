"""Tests for the embedding provider abstraction."""

import asyncio
import json

import httpx
import pytest

from ..embedding.interface import EmbeddingError
from ..embedding.ollama import OllamaEmbeddingProvider


class _EmbeddingHandler(httpx.MockTransport):
    def __init__(self, *, fail: bool = False, wrong_count: bool = False) -> None:
        super().__init__(handler=self._handler)
        self._fail = fail
        self._wrong_count = wrong_count
        self.calls = 0

    def _handler(self, request: httpx.Request) -> httpx.Response:
        self.calls += 1
        if self._fail:
            raise httpx.ConnectError("embedding provider down")
        payload = json.loads(request.content)
        texts = payload.get("input", [])
        if self._wrong_count:
            embeddings = [[1.0, 0.0] for _ in texts]
            embeddings = embeddings[:1]  # wrong count
        else:
            embeddings = [[float(i + 1), 0.0] for i in range(len(texts))]
        return httpx.Response(
            200,
            json={"model": payload.get("model"), "embeddings": embeddings},
        )


def test_provider_embeds_texts():
    transport = _EmbeddingHandler()
    provider = OllamaEmbeddingProvider(
        base_url="http://ollama:11434", model="nomic-embed-text", transport=transport
    )
    vectors = asyncio.run(provider.embed(["alpha", "beta"]))
    assert len(vectors) == 2
    assert len(vectors[0]) == 2
    assert provider.model_id == "nomic-embed-text"


def test_provider_empty_input_returns_empty():
    provider = OllamaEmbeddingProvider(
        base_url="http://ollama:11434", model="m", transport=_EmbeddingHandler()
    )
    assert asyncio.run(provider.embed([])) == []


def test_provider_failure_raises_embedding_error():
    transport = _EmbeddingHandler(fail=True)
    provider = OllamaEmbeddingProvider(
        base_url="http://ollama:11434",
        model="m",
        retry_attempts=2,
        retry_base_seconds=0.0,
        transport=transport,
    )
    with pytest.raises(EmbeddingError):
        asyncio.run(provider.embed(["x"]))


def test_provider_wrong_count_raises():
    transport = _EmbeddingHandler(wrong_count=True)
    provider = OllamaEmbeddingProvider(
        base_url="http://ollama:11434", model="m", transport=transport
    )
    with pytest.raises(EmbeddingError):
        asyncio.run(provider.embed(["x", "y"]))


def test_provider_model_required():
    with pytest.raises(ValueError):
        OllamaEmbeddingProvider(base_url="http://x", model="  ")
