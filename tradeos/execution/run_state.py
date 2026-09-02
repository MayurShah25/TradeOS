"""Deterministic state for one governed paper-trading run."""

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum


class PaperRunStatus(StrEnum):
    """Lifecycle states for a paper-trading run."""

    OPEN = "OPEN"
    RECONCILIATION_REQUIRED = "RECONCILIATION_REQUIRED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass(frozen=True, slots=True)
class PaperTradingRun:
    """Immutable identity and lifecycle state for one trading attempt."""

    run_id: str
    proposal_id: str
    risk_decision_id: str
    authorization_id: str
    account_id: str
    instrument_id: str
    configuration_hash: str
    started_at: datetime
    status: PaperRunStatus = PaperRunStatus.OPEN
    completed_at: datetime | None = None

    def validate(self) -> None:
        """Validate stable run identity and lifecycle invariants."""
        for name, value in (
            ("run_id", self.run_id),
            ("proposal_id", self.proposal_id),
            ("risk_decision_id", self.risk_decision_id),
            ("authorization_id", self.authorization_id),
            ("account_id", self.account_id),
            ("instrument_id", self.instrument_id),
            ("configuration_hash", self.configuration_hash),
        ):
            if not value:
                raise ValueError(f"{name} must not be empty")
        if self.started_at.tzinfo is None or self.started_at.utcoffset() is None:
            raise ValueError("started_at must be timezone-aware")
        if self.started_at.tzinfo is not UTC:
            raise ValueError("started_at must use UTC")
        if self.completed_at is not None:
            if self.completed_at.tzinfo is None or self.completed_at.utcoffset() is None:
                raise ValueError("completed_at must be timezone-aware")
            if self.completed_at.tzinfo is not UTC:
                raise ValueError("completed_at must use UTC")
            if self.completed_at < self.started_at:
                raise ValueError("completed_at cannot precede started_at")
        if self.status in (PaperRunStatus.OPEN, PaperRunStatus.RECONCILIATION_REQUIRED):
            if self.completed_at is not None:
                raise ValueError("non-terminal run cannot have completed_at")
        elif self.completed_at is None:
            raise ValueError("closed run must have completed_at")

    def complete(self, completed_at: datetime) -> "PaperTradingRun":
        """Return a completed run without mutating the original."""
        self._validate_terminal_transition(completed_at)
        return self._closed(PaperRunStatus.COMPLETED, completed_at)

    def fail(self, completed_at: datetime) -> "PaperTradingRun":
        """Return a failed run without mutating the original."""
        self._validate_terminal_transition(completed_at)
        return self._closed(PaperRunStatus.FAILED, completed_at)

    def require_reconciliation(self) -> "PaperTradingRun":
        """Return a non-terminal run state that explicitly requires reconciliation."""
        self.validate()
        if self.status is not PaperRunStatus.OPEN:
            raise ValueError("paper run is not open")
        return PaperTradingRun(
            run_id=self.run_id,
            proposal_id=self.proposal_id,
            risk_decision_id=self.risk_decision_id,
            authorization_id=self.authorization_id,
            account_id=self.account_id,
            instrument_id=self.instrument_id,
            configuration_hash=self.configuration_hash,
            started_at=self.started_at,
            status=PaperRunStatus.RECONCILIATION_REQUIRED,
        )

    def _closed(self, status: PaperRunStatus, completed_at: datetime) -> "PaperTradingRun":
        return PaperTradingRun(
            run_id=self.run_id,
            proposal_id=self.proposal_id,
            risk_decision_id=self.risk_decision_id,
            authorization_id=self.authorization_id,
            account_id=self.account_id,
            instrument_id=self.instrument_id,
            configuration_hash=self.configuration_hash,
            started_at=self.started_at,
            status=status,
            completed_at=completed_at,
        )

    def _validate_terminal_transition(self, completed_at: datetime) -> None:
        self.validate()
        if self.status not in (PaperRunStatus.OPEN, PaperRunStatus.RECONCILIATION_REQUIRED):
            raise ValueError("paper run is already closed")
        if completed_at.tzinfo is None or completed_at.utcoffset() is None:
            raise ValueError("completed_at must be timezone-aware")
        if completed_at.tzinfo is not UTC:
            raise ValueError("completed_at must use UTC")
        if completed_at < self.started_at:
            raise ValueError("completed_at cannot precede started_at")
