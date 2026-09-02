"""Execution ports separating core order intent from broker implementations."""

from abc import ABC, abstractmethod
from typing import Protocol

from .audit import AuditEvent
from .models import Order, OrderStatus
from .run_state import PaperRunStatus, PaperTradingRun


class BrokerExecutionPort(ABC):
    """Boundary for broker order submission."""

    @abstractmethod
    def submit(self, order: Order) -> OrderStatus:
        """Submit a validated order and return its normalized status."""
        raise NotImplementedError


class PaperTradingPersistencePort(Protocol):
    """Persistence contract required by a governed paper-trading session."""

    def save_run(self, run: PaperTradingRun) -> None:
        """Persist the current immutable run snapshot."""
        ...

    def get_run(self, run_id: str) -> PaperTradingRun | None:
        """Return a persisted run snapshot when it exists."""
        ...

    def list_runs(
        self,
        *,
        status: PaperRunStatus | None = None,
        account_id: str | None = None,
        instrument_id: str | None = None,
    ) -> tuple[PaperTradingRun, ...]:
        """Return persisted runs matching the supplied filters."""
        ...

    def append_audit_event(self, event: AuditEvent) -> None:
        """Append one immutable audit event."""
        ...

    def audit_events(self, run_id: str) -> tuple[AuditEvent, ...]:
        """Return the immutable audit history for a run."""
        ...
