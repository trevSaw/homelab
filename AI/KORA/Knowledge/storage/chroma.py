"""Chroma v2 vector store adapter.

Chroma is infrastructure/indexing; it is never the Knowledge authority. This
adapter keeps Chroma-specific logic behind the ``VectorStore`` abstraction so the
rest of KORA depends only on the abstraction. A ``transport`` may be injected for
tests (mirrors the Honcho adapter pattern).
"""

from __future__ import annotations

import logging

import httpx

from .vector import (
    VectorResult,
    VectorStoreError,
    VectorStoreUnavailableError,
)

log = logging.getLogger("kora.knowledge.chroma")

_DEFAULT_TENANT = "default_tenant"
_DEFAULT_DATABASE = "default_database"


class ChromaVectorStore:
    def __init__(
        self,
        *,
        base_url: str,
        collection: str,
        tenant: str = _DEFAULT_TENANT,
        database: str = _DEFAULT_DATABASE,
        timeout_seconds: float = 30.0,
        retry_attempts: int = 2,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        if not collection.strip():
            raise ValueError("collection name is required")
        self._base_url = base_url.rstrip("/")
        self._collection_name = collection
        self._tenant = tenant
        self._database = database
        self._timeout = timeout_seconds
        self._retry_attempts = max(1, retry_attempts)
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self._timeout),
            transport=transport,
        )
        self._collection_id: str | None = None

    async def close(self) -> None:
        await self._client.aclose()

    async def health(self) -> bool:
        try:
            response = await self._request("GET", "/api/v2/heartbeat")
            return response.status_code == 200
        except VectorStoreError:
            return False

    async def _ensure_collection(self) -> str:
        if self._collection_id:
            return self._collection_id
        path = f"/api/v2/tenants/{self._tenant}/databases/{self._database}/collections"
        response = await self._request(
            "POST",
            path,
            json={"name": self._collection_name, "get_or_create": True},
        )
        payload = response.json()
        collection_id = (payload or {}).get("id")
        if not collection_id:
            raise VectorStoreError("chroma returned a collection without an id")
        self._collection_id = collection_id
        return collection_id

    async def upsert(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict],
    ) -> None:
        if not (len(ids) == len(embeddings) == len(documents) == len(metadatas)):
            raise VectorStoreError("upsert arguments must have equal lengths")
        collection_id = await self._ensure_collection()
        path = (
            f"/api/v2/tenants/{self._tenant}/databases/{self._database}"
            f"/collections/{collection_id}/upsert"
        )
        await self._request(
            "POST",
            path,
            json={
                "ids": ids,
                "embeddings": embeddings,
                "documents": documents,
                "metadatas": metadatas,
            },
        )

    async def query(
        self,
        query_embedding: list[float],
        *,
        top_k: int,
        where: dict | None = None,
    ) -> list[VectorResult]:
        collection_id = await self._ensure_collection()
        path = (
            f"/api/v2/tenants/{self._tenant}/databases/{self._database}"
            f"/collections/{collection_id}/query"
        )
        payload: dict = {
            "query_embeddings": [query_embedding],
            "n_results": max(1, top_k),
            "include": ["metadatas", "documents", "distances"],
        }
        if where:
            payload["where"] = where
        response = await self._request("POST", path, json=payload)
        data = response.json() or {}
        ids = (data.get("ids") or [[]])[0]
        documents = (data.get("documents") or [[]])[0]
        metadatas = (data.get("metadatas") or [[]])[0]
        distances = (data.get("distances") or [[]])[0]
        results: list[VectorResult] = []
        for i, _id in enumerate(ids):
            results.append(
                VectorResult(
                    id=str(_id),
                    document=str(documents[i]) if i < len(documents) else "",
                    metadata=dict(metadatas[i]) if i < len(metadatas) else {},
                    distance=float(distances[i]) if i < len(distances) else 0.0,
                )
            )
        return results

    async def delete(self, ids: list[str]) -> None:
        collection_id = await self._ensure_collection()
        path = (
            f"/api/v2/tenants/{self._tenant}/databases/{self._database}"
            f"/collections/{collection_id}/delete"
        )
        await self._request("POST", path, json={"ids": ids})

    async def count(self) -> int:
        collection_id = await self._ensure_collection()
        path = (
            f"/api/v2/tenants/{self._tenant}/databases/{self._database}"
            f"/collections/{collection_id}/count"
        )
        response = await self._request("GET", path)
        return int(response.json() or 0)

    async def _request(self, method: str, path: str, **kwargs: object) -> httpx.Response:
        last_error: Exception | None = None
        for _ in range(self._retry_attempts):
            try:
                response = await self._client.request(method, f"{self._base_url}{path}", **kwargs)
                if response.status_code < 400:
                    return response
                raise VectorStoreError(
                    f"chroma rejected request: HTTP {response.status_code}"
                )
            except VectorStoreError:
                raise
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                last_error = exc
        raise VectorStoreUnavailableError("chroma unavailable after retries") from last_error
