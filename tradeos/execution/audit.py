"""Immutable audit records for governed paper trading."""

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum


class AuditEventType(StrEnum):
    """Canonical events recorded during a paper-trading run."""

    RUN_STARTED = "RUN_STARTED"
    RISK_EVALUATED = "RISK_EVALUATED"
    AUTHORIZATION_VERIFIED = "AUTHORIZATION_VERIFIED"
    EXECUTION_SUBMITTED = "EXECUTION_SUBMITTED"
    EXECUTION_RECONCILED = "EXECUTION_RECONCILED"
    PORTFOLIO_UPDATED = "PORTFOLIO_UPDATED"
    RUN_COMPLETED = "RUN_COMPLETED"
    RUN_FAILED = "RUN_FAILED"


@dataclass(frozen=True, slots=True)
class AuditEvent:
    """Immutable, append-only audit record."""

    event_id: str
    run_id: str
    event_type: AuditEventType
    occurred_at: datetime
    sequence: int
    payload: tuple[tuple[str, str], ...] = ()

    def validate(self) -> None:
        """Validate audit invariants before recording an event."""
        if not self.event_id:
            raise ValueError("event_id must not be empty")
        if not self.run_id:
            raise ValueError("run_id must not be empty")
        if self.sequence < 0:
            raise ValueError("sequence cannot be negative")
        if self.occurred_at.tzinfo is None or self.occurred_at.utcoffset() is None:
            raise ValueError("occurred_at must be timezone-aware")
        if self.occurred_at.tzinfo is not UTC:
            raise ValueError("occurred_at must use UTC")
        keys = [key for key, _ in self.payload]
        if any(not key for key in keys):
            raise ValueError("payload keys must not be empty")
        if len(keys) != len(set(keys)):
            raise ValueError("payload keys must be unique")


class AuditTrail:
    """Append-only in-memory audit trail with deterministic ordering."""

    def __init__(self) -> None:
        self._events: dict[str, list[AuditEvent]] = {}

    def append(self, event: AuditEvent) -> None:
        """Append an event, rejecting duplicate IDs and invalid sequence numbers."""
        event.validate()
        events = self._events.setdefault(event.run_id, [])
        if any(existing.event_id == event.event_id for existing in events):
            raise ValueError("duplicate event_id")
        expected_sequence = len(events)
        if event.sequence != expected_sequence:
            raise ValueError("audit sequence must be contiguous")
        events.append(event)

    def events(self, run_id: str) -> tuple[AuditEvent, ...]:
        """Return the immutable ordered event history for a run."""
        if not run_id:
            raise ValueError("run_id must not be empty")
        return tuple(self._events.get(run_id, ()))
