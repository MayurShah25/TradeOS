from datetime import datetime, timezone

import pytest

from tradeos.contracts import Command, Event


def test_command_is_immutable() -> None:
    command = Command(
        command_id="cmd-1",
        command_type="risk.evaluate",
        aggregate_id="proposal-1",
        issued_at=datetime.now(timezone.utc),
        payload={"symbol": "AAPL"},
        correlation_id="corr-1",
    )

    with pytest.raises(AttributeError):
        command.command_type = "changed"  # type: ignore[misc]


def test_event_defaults_and_causation() -> None:
    event = Event(
        event_id="evt-1",
        event_type="risk.approved",
        aggregate_id="proposal-1",
        occurred_at=datetime.now(timezone.utc),
        payload={},
        correlation_id="corr-1",
        causation_id="cmd-1",
    )

    assert event.version == 1
    assert event.causation_id == "cmd-1"


def test_event_version_must_be_positive() -> None:
    with pytest.raises(ValueError, match="event version must be >= 1"):
        Event(
            event_id="evt-1",
            event_type="risk.approved",
            aggregate_id="proposal-1",
            occurred_at=datetime.now(timezone.utc),
            payload={},
            correlation_id="corr-1",
            version=0,
        )
