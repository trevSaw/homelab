"""Honcho v3 adapter implementing the provider-neutral durable Memory contract.

No other runtime component contains Honcho endpoints or wire schemas.
"""

from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import httpx

from .durable_memory import (
    DisabledDurableMemoryStore,
    DurableMemory,
    DurableMemoryError,
    DurableMemoryStore,
)
from .memory_models import MemoryProposal

_ENVELOPE_PREFIX = "KORA_MEMORY_V1:"


@dataclass(frozen=True, slots=True)
class HonchoAdapterConfig:
    base_url: str
    workspace_id: str
    observer_id: str
    observed_id: str
    bearer_token: str | None = None
    timeout_seconds: float = 10.0
    retry_attempts: int = 3
    retry_base_seconds: float = 0.2


class HonchoAdapter(DurableMemoryStore):
    """Direct-conclusion adapter; sessions and automatic derivation are unused."""

    def __init__(
        self,
        config: HonchoAdapterConfig,
        *,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._config = config
        headers = {"Accept": "application/json"}
        if config.bearer_token:
            headers["Authorization"] = f"Bearer {config.bearer_token}"
        self._client = httpx.AsyncClient(
            base_url=config.base_url.rstrip("/"),
            headers=headers,
            timeout=config.timeout_seconds,
            transport=transport,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def health(self) -> bool:
        try:
            response = await self._request("GET", "/health")
            return response.status_code == 200
        except DurableMemoryError:
            return False

    async def commit(self, proposal: MemoryProposal, content: str) -> DurableMemory:
        existing = await self.find_by_proposal_id(proposal.proposal_id)
        if existing is not None:
            return existing

        envelope = _serialize(proposal, content)
        response = await self._request(
            "POST",
            self._conclusions_path,
            json={
                "conclusions": [
                    {
                        "content": envelope,
                        "observer_id": self._config.observer_id,
                        "observed_id": self._config.observed_id,
                    }
                ]
            },
        )
        payload = response.json()
        items = payload if isinstance(payload, list) else payload.get("items", [])
        if not items:
            raise DurableMemoryError("persistence backend returned no conclusion")
        return _deserialize(items[0])

    async def find_by_proposal_id(self, proposal_id: str) -> DurableMemory | None:
        for memory in await self.list_memories(limit=100):
            if memory.proposal_id == proposal_id:
                return memory
        return None

    async def list_memories(
        self,
        *,
        category: str | None = None,
        limit: int = 100,
    ) -> list[DurableMemory]:
        response = await self._request(
            "POST",
            f"{self._conclusions_path}/list",
            params={"page": 1, "size": min(max(limit, 1), 100)},
            json={
                "filters": {
                    "observer_id": self._config.observer_id,
                    "observed_id": self._config.observed_id,
                }
            },
        )
        payload = response.json()
        if isinstance(payload, list):
            items = payload
        else:
            items = payload.get("items") or payload.get("data") or []
        result: list[DurableMemory] = []
        for item in items:
            try:
                memory = _deserialize(item)
            except (KeyError, TypeError, ValueError, json.JSONDecodeError):
                continue
            if category is None or memory.category == category:
                result.append(memory)
        return result[:limit]

    async def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        last_error: Exception | None = None
        for attempt in range(self._config.retry_attempts):
            try:
                response = await self._client.request(method, path, **kwargs)
                if response.status_code < 400:
                    return response
                if response.status_code not in {408, 429} and response.status_code < 500:
                    raise DurableMemoryError(
                        f"persistence backend rejected request: HTTP {response.status_code}"
                    )
                last_error = DurableMemoryError(
                    f"transient persistence error: HTTP {response.status_code}"
                )
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                last_error = exc
            if attempt + 1 < self._config.retry_attempts:
                await asyncio.sleep(self._config.retry_base_seconds * (2**attempt))
        raise DurableMemoryError("persistence backend unavailable after retries") from last_error

    @property
    def _conclusions_path(self) -> str:
        return f"/v3/workspaces/{self._config.workspace_id}/conclusions"


def durable_store_from_config(config: dict[str, Any]) -> DurableMemoryStore:
    """Composition boundary that keeps backend details inside this adapter."""
    backend = config.get("honcho") or {}
    if not backend.get("enabled") or not backend.get("durable_writes"):
        return DisabledDurableMemoryStore()
    return HonchoAdapter(
        HonchoAdapterConfig(
            base_url=os.environ.get(
                "KORA_HONCHO_BASE_URL",
                str(backend.get("endpoint") or "http://honcho-api:8000"),
            ),
            workspace_id=os.environ.get(
                "KORA_HONCHO_WORKSPACE_ID",
                str(backend.get("workspace_id") or "kora"),
            ),
            observer_id=os.environ.get(
                "KORA_HONCHO_OBSERVER_ID",
                str(backend.get("observer_id") or "kora"),
            ),
            observed_id=os.environ.get(
                "KORA_HONCHO_OBSERVED_ID",
                str(backend.get("observed_id") or "user"),
            ),
            bearer_token=os.environ.get("KORA_HONCHO_BEARER_TOKEN") or None,
            timeout_seconds=float(backend.get("timeout_seconds", 10)),
            retry_attempts=int(backend.get("retry_attempts", 3)),
            retry_base_seconds=float(backend.get("retry_base_seconds", 0.2)),
        )
    )


def _serialize(proposal: MemoryProposal, content: str) -> str:
    value = {
        "schema_version": "1.0",
        "proposal_id": proposal.proposal_id,
        "content": content,
        "category": proposal.candidate_type,
        "source": proposal.source,
        "conversation_id": proposal.conversation_id,
        "confidence": proposal.confidence,
        "importance": proposal.importance,
        "related_entities": proposal.related_entities,
        "related_topics": proposal.related_topics,
        "approved_at": datetime.now(timezone.utc).isoformat(),
    }
    return _ENVELOPE_PREFIX + json.dumps(value, sort_keys=True, separators=(",", ":"))


def _deserialize(value: dict[str, Any]) -> DurableMemory:
    raw = str(value["content"])
    if not raw.startswith(_ENVELOPE_PREFIX):
        raise ValueError("not a KORA durable Memory envelope")
    envelope = json.loads(raw[len(_ENVELOPE_PREFIX) :])
    created_at = value.get("created_at") or envelope["approved_at"]
    return DurableMemory(
        memory_id=str(value["id"]),
        proposal_id=str(envelope["proposal_id"]),
        content=str(envelope["content"]),
        category=str(envelope["category"]),
        source=str(envelope["source"]),
        conversation_id=envelope.get("conversation_id"),
        confidence=float(envelope["confidence"]),
        importance=float(envelope["importance"]),
        related_entities=tuple(envelope.get("related_entities") or []),
        related_topics=tuple(envelope.get("related_topics") or []),
        created_at=datetime.fromisoformat(str(created_at)),
    )
