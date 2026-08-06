"""Transport-neutral internal event bus contracts and in-process adapter."""

from __future__ import annotations

import logging
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Protocol

log = logging.getLogger("kora.event_bus")

EventHandler = Callable[["EventEnvelope"], None]
EventFilter = Callable[["EventEnvelope"], bool]


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class EventEnvelope:
    """Serializable event contract shared by all KORA components."""

    event_type: str
    source: str
    payload: dict[str, Any]
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=_utc_now)
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metadata: dict[str, Any] = field(default_factory=dict)
    schema_version: str = "1.0"

    def __post_init__(self) -> None:
        if not self.event_type.strip():
            raise ValueError("event_type is required")
        if not self.source.strip():
            raise ValueError("source is required")
        if not isinstance(self.payload, dict):
            raise TypeError("payload must be a dictionary")
        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary")
        object.__setattr__(self, "timestamp", _as_utc(self.timestamp))

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation suitable for future transports."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "schema_version": self.schema_version,
            "metadata": self.metadata,
            "payload": self.payload,
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "EventEnvelope":
        """Rehydrate a serialized envelope without depending on this adapter."""
        return cls(
            event_id=str(value["event_id"]),
            event_type=str(value["event_type"]),
            source=str(value["source"]),
            timestamp=datetime.fromisoformat(str(value["timestamp"])),
            correlation_id=str(value["correlation_id"]),
            schema_version=str(value.get("schema_version", "1.0")),
            metadata=dict(value.get("metadata") or {}),
            payload=dict(value.get("payload") or {}),
        )


@dataclass(frozen=True, slots=True)
class Subscription:
    subscription_id: str
    event_type: str


class EventBus(Protocol):
    """Stable interface; adapters may be in-process or distributed."""

    def publish(self, event: EventEnvelope) -> int: ...

    def subscribe(
        self,
        event_type: str,
        handler: EventHandler,
        event_filter: EventFilter | None = None,
    ) -> Subscription: ...

    def unsubscribe(self, subscription: Subscription) -> bool: ...


@dataclass(slots=True)
class _RegisteredSubscription:
    subscription: Subscription
    handler: EventHandler
    event_filter: EventFilter | None


class InProcessEventBus:
    """Synchronous adapter used by Phase 14.2A.

    Consumers depend on EventBus and EventEnvelope only. Delivery timing, object
    identity, and shared memory are intentionally absent from the contract.
    """

    def __init__(self) -> None:
        self._subscriptions: dict[str, _RegisteredSubscription] = {}
        self._lock = threading.RLock()

    def publish(self, event: EventEnvelope) -> int:
        if not isinstance(event, EventEnvelope):
            raise TypeError("publish requires an EventEnvelope")
        # Serialization is checked at the boundary so a future transport can
        # accept every event currently accepted by this adapter.
        import json

        json.dumps(event.to_dict())
        with self._lock:
            subscriptions = tuple(self._subscriptions.values())

        delivered = 0
        for registered in subscriptions:
            if not _topic_matches(registered.subscription.event_type, event.event_type):
                continue
            try:
                if registered.event_filter and not registered.event_filter(event):
                    continue
                registered.handler(event)
                delivered += 1
            except Exception:  # noqa: BLE001
                log.exception(
                    "subscriber failed event_type=%s subscription_id=%s correlation_id=%s",
                    event.event_type,
                    registered.subscription.subscription_id,
                    event.correlation_id,
                )
        return delivered

    def subscribe(
        self,
        event_type: str,
        handler: EventHandler,
        event_filter: EventFilter | None = None,
    ) -> Subscription:
        if not event_type.strip():
            raise ValueError("event_type is required")
        if not callable(handler):
            raise TypeError("handler must be callable")
        subscription = Subscription(str(uuid.uuid4()), event_type)
        registered = _RegisteredSubscription(subscription, handler, event_filter)
        with self._lock:
            self._subscriptions[subscription.subscription_id] = registered
        return subscription

    def unsubscribe(self, subscription: Subscription) -> bool:
        with self._lock:
            return self._subscriptions.pop(subscription.subscription_id, None) is not None


def _topic_matches(subscription_type: str, event_type: str) -> bool:
    if subscription_type == "*":
        return True
    if subscription_type.endswith(".*"):
        return event_type.startswith(subscription_type[:-1])
    return subscription_type == event_type
