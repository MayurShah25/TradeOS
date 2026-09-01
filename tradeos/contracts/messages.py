"""Transport-independent TradeOS command and event contracts."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class Command:
    """Request an action; a command does not itself grant authority."""

    command_id: str
    command_type: str
    aggregate_id: str
    issued_at: datetime
    payload: dict[str, Any]
    correlation_id: str


@dataclass(frozen=True, slots=True)
class Event:
    """Record a fact; an event does not authorize a new privileged action."""

    event_id: str
    event_type: str
    aggregate_id: str
    occurred_at: datetime
    payload: dict[str, Any]
    correlation_id: str
    causation_id: str | None = None
    version: int = 1

    def __post_init__(self) -> None:
        if self.version < 1:
            raise ValueError("event version must be >= 1")
