"""Ollama-backed embedding provider.

Phase 14.3 uses an Ollama-backed embedding provider. The model is
configuration-driven (``KORA_EMBEDDING_MODEL``) and is not hard-coded into the
Knowledge architecture. A ``transport`` may be injected for tests.
"""

from __future__ import annotations

import asyncio
import logging

import httpx

from .interface import EmbeddingError, EmbeddingProvider

log = logging.getLogger("kora.knowledge.embedding")


class OllamaEmbeddingProvider:
    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        timeout_seconds: float = 60.0,
        retry_attempts: int = 2,
        retry_base_seconds: float = 0.2,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        if not model.strip():
            raise ValueError("embedding model is required")
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_seconds
        self._retry_attempts = max(1, retry_attempts)
        self._retry_base = retry_base_seconds
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self._timeout),
            transport=transport,
        )

    @property
    def model_id(self) -> str:
        return self._model

    async def close(self) -> None:
        await self._client.aclose()

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        last_error: Exception | None = None
        for attempt in range(self._retry_attempts):
            try:
                response = await self._client.post(
                    f"{self._base_url}/api/embed",
                    json={"model": self._model, "input": texts},
                )
                if response.status_code >= 400:
                    raise EmbeddingError(
                        f"embedding provider rejected request: HTTP {response.status_code}"
                    )
                payload = response.json()
                embeddings = payload.get("embeddings")
                if not isinstance(embeddings, list) or len(embeddings) != len(texts):
                    raise EmbeddingError("embedding provider returned unexpected payload")
                return [[float(value) for value in vector] for vector in embeddings]
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                last_error = exc
            except EmbeddingError:
                raise
            except Exception as exc:  # noqa: BLE001
                log.warning("embedding request failed: %s", exc)
                last_error = exc
            if attempt + 1 < self._retry_attempts:
                await asyncio.sleep(self._retry_base * (2**attempt))
        raise EmbeddingError(f"embedding provider unavailable after retries") from last_error
