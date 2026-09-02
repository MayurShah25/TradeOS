import datetime as dt

import pytest

from tradeos.execution import AuditEvent, AuditEventType, AuditTrail


NOW = dt.datetime(2026, 1, 1, 10, tzinfo=dt.UTC)


def event(event_id: str, sequence: int) -> AuditEvent:
    return AuditEvent(
        event_id=event_id,
        run_id="run-1",
        event_type=AuditEventType.RUN_STARTED,
        occurred_at=NOW,
        sequence=sequence,
        payload=(("order_id", "order-1"),),
    )


def test_audit_trail_preserves_append_order_and_is_immutable() -> None:
    trail = AuditTrail()
    trail.append(event("event-1", 0))
    trail.append(event("event-2", 1))

    events = trail.events("run-1")
    assert tuple(item.event_id for item in events) == ("event-1", "event-2")
    assert isinstance(events, tuple)


def test_audit_trail_rejects_duplicate_event_ids() -> None:
    trail = AuditTrail()
    trail.append(event("event-1", 0))

    with pytest.raises(ValueError, match="duplicate"):
        trail.append(event("event-1", 1))


def test_audit_trail_rejects_sequence_gaps() -> None:
    trail = AuditTrail()

    with pytest.raises(ValueError, match="contiguous"):
        trail.append(event("event-2", 1))


def test_audit_trail_keeps_runs_separate() -> None:
    trail = AuditTrail()
    trail.append(event("event-1", 0))
    other = AuditEvent(
        event_id="event-9",
        run_id="run-2",
        event_type=AuditEventType.RUN_STARTED,
        occurred_at=NOW,
        sequence=0,
    )
    trail.append(other)

    assert len(trail.events("run-1")) == 1
    assert len(trail.events("run-2")) == 1


def test_audit_event_rejects_non_utc_timestamp() -> None:
    timestamp = NOW.astimezone(dt.timezone(dt.timedelta(hours=1)))
    invalid = AuditEvent(
        event_id="event-1",
        run_id="run-1",
        event_type=AuditEventType.RUN_STARTED,
        occurred_at=timestamp,
        sequence=0,
    )

    with pytest.raises(ValueError, match="UTC"):
        invalid.validate()
