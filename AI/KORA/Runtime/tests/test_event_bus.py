from __future__ import annotations

import json
import unittest

from app.event_bus import EventEnvelope, InProcessEventBus


class EventBusTests(unittest.TestCase):
    def test_envelope_round_trip_is_json_serializable(self) -> None:
        original = EventEnvelope(
            event_type="git.commit",
            source="git-mcp",
            payload={"sha": "abc123"},
            metadata={"repository": "homelab"},
            correlation_id="corr-1",
        )

        encoded = json.dumps(original.to_dict())
        restored = EventEnvelope.from_dict(json.loads(encoded))

        self.assertEqual(restored, original)

    def test_publish_routes_by_namespace_and_filter(self) -> None:
        bus = InProcessEventBus()
        received: list[str] = []
        bus.subscribe(
            "conversation.*",
            lambda event: received.append(event.event_type),
            lambda event: event.metadata.get("eligible") is True,
        )
        bus.subscribe("git.*", lambda event: received.append(event.event_type))

        self.assertEqual(
            bus.publish(
                EventEnvelope(
                    event_type="conversation.message",
                    source="kora",
                    payload={"text": "hello"},
                    metadata={"eligible": True},
                )
            ),
            1,
        )
        self.assertEqual(
            bus.publish(
                EventEnvelope(
                    event_type="conversation.summary",
                    source="kora",
                    payload={"text": "summary"},
                    metadata={"eligible": False},
                )
            ),
            0,
        )
        self.assertEqual(received, ["conversation.message"])

    def test_unsubscribe_stops_delivery(self) -> None:
        bus = InProcessEventBus()
        received: list[str] = []
        subscription = bus.subscribe("*", lambda event: received.append(event.event_id))
        self.assertTrue(bus.unsubscribe(subscription))
        self.assertFalse(bus.unsubscribe(subscription))

        delivered = bus.publish(
            EventEnvelope(event_type="docker.container_started", source="docker-mcp", payload={})
        )

        self.assertEqual(delivered, 0)
        self.assertEqual(received, [])

    def test_subscriber_failure_isolated(self) -> None:
        bus = InProcessEventBus()
        received: list[str] = []

        def fail(_: EventEnvelope) -> None:
            raise RuntimeError("subscriber failed")

        bus.subscribe("calendar.updated", fail)
        bus.subscribe("calendar.updated", lambda event: received.append(event.event_id))
        event = EventEnvelope(event_type="calendar.updated", source="calendar-mcp", payload={})

        self.assertEqual(bus.publish(event), 1)
        self.assertEqual(received, [event.event_id])


if __name__ == "__main__":
    unittest.main()
