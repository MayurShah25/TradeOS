"""Deterministic ordered market-data stream boundary for paper trading."""

from dataclasses import dataclass
from datetime import datetime

from tradeos.market_data import PaperMarketDataSnapshot


@dataclass(frozen=True, slots=True)
class PaperMarketDataStreamState:
    """Immutable state representing the last accepted observation."""

    instrument_id: str
    source_id: str
    last_observed_at: datetime
    last_snapshot: PaperMarketDataSnapshot


class PaperMarketDataStream:
    """Accept only valid, ordered observations for one instrument/source."""

    def __init__(self, *, instrument_id: str, source_id: str) -> None:
        if not instrument_id.strip():
            raise ValueError("instrument_id must not be blank")
        if not source_id.strip():
            raise ValueError("source_id must not be blank")
        self._instrument_id = instrument_id
        self._source_id = source_id
        self._last_snapshot: PaperMarketDataSnapshot | None = None

    @property
    def state(self) -> PaperMarketDataStreamState | None:
        if self._last_snapshot is None:
            return None
        return PaperMarketDataStreamState(
            instrument_id=self._instrument_id,
            source_id=self._source_id,
            last_observed_at=self._last_snapshot.observed_at,
            last_snapshot=self._last_snapshot,
        )

    def accept(self, snapshot: PaperMarketDataSnapshot) -> None:
        """Accept a strictly newer valid snapshot; reject invalid/out-of-order data."""
        snapshot.validate()
        if snapshot.instrument_id != self._instrument_id:
            raise ValueError("market-data instrument does not match stream")
        if snapshot.source_id != self._source_id:
            raise ValueError("market-data source does not match stream")
        if (\n            self._last_snapshot is not None\n            and snapshot.observed_at <= self._last_snapshot.observed_at\n        ):
            raise ValueError("market-data observation is duplicate or out of order")
        self._last_snapshot = snapshot

    def latest(self) -> PaperMarketDataSnapshot | None:
        """Return the latest accepted immutable observation."""
        return self._last_snapshot