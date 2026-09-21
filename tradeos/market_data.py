"""Deterministic market-data integrity boundary for paper trading."""

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class PaperMarketDataSnapshot:
    """Immutable price observation suitable for governed paper workflows."""

    instrument_id: str
    price: Decimal
    observed_at: datetime
    source_id: str

    def validate(self) -> None:
        """Validate identity, price, and timestamp invariants."""
        if not self.instrument_id.strip():
            raise ValueError("instrument_id must not be blank")
        if not self.source_id.strip():
            raise ValueError("source_id must not be blank")
        if self.price <= 0:
            raise ValueError("price must be greater than zero")
        if self.observed_at.tzinfo is None or self.observed_at.utcoffset() is None:
            raise ValueError("observed_at must be timezone-aware")
        if self.observed_at.tzinfo is not UTC:
            raise ValueError("observed_at must use UTC")


@dataclass(frozen=True, slots=True)
class PaperMarketDataFreshnessPolicy:
    """Explicit maximum observation age for paper workflows."""

    max_age_seconds: int

    def validate(self) -> None:
        if self.max_age_seconds < 0:
            raise ValueError("max_age_seconds must not be negative")


def validate_paper_market_data(
    snapshot: PaperMarketDataSnapshot,
    *,
    instrument_id: str,
    observed_at: datetime,
    policy: PaperMarketDataFreshnessPolicy,
) -> None:
    """Fail closed when a snapshot is invalid, mismatched, future-dated, or stale."""
    snapshot.validate()
    policy.validate()

    if not instrument_id.strip():
        raise ValueError("instrument_id must not be blank")
    if observed_at.tzinfo is None or observed_at.utcoffset() is None:
        raise ValueError("validation time must be timezone-aware")
    if observed_at.tzinfo is not UTC:
        raise ValueError("validation time must use UTC")
    if snapshot.instrument_id != instrument_id:
        raise ValueError("market-data instrument does not match requested instrument")

    age_seconds = (observed_at - snapshot.observed_at).total_seconds()
    if age_seconds < 0:
        raise ValueError("market-data observation cannot be from the future")
    if age_seconds > policy.max_age_seconds:
        raise ValueError("market-data snapshot is stale")
