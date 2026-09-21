"""In-memory persistence for immutable paper market-data snapshots."""

from datetime import datetime

from tradeos.market_data import PaperMarketDataSnapshot
from tradeos.market_data_repository import PaperMarketDataRepository


class InMemoryPaperMarketDataRepository(PaperMarketDataRepository):
    """Deterministic repository useful for tests and local paper workflows."""

    def __init__(self) -> None:
        self._snapshots: dict[tuple[str, str, datetime], PaperMarketDataSnapshot] = {}

    def save(self, snapshot: PaperMarketDataSnapshot) -> None:
        snapshot.validate()
        key = (snapshot.instrument_id, snapshot.source_id, snapshot.observed_at)
        existing = self._snapshots.get(key)
        if existing is not None and existing != snapshot:
            raise ValueError("paper market-data snapshot is immutable")
        self._snapshots[key] = snapshot

    def get(
        self,
        *,
        instrument_id: str,
        source_id: str,
        observed_at: datetime,
    ) -> PaperMarketDataSnapshot | None:
        if not instrument_id.strip():
            raise ValueError("instrument_id must not be blank")
        if not source_id.strip():
            raise ValueError("source_id must not be blank")
        return self._snapshots.get((instrument_id, source_id, observed_at))

    def list_for_instrument(
        self,
        *,
        instrument_id: str,
        source_id: str | None = None,
    ) -> tuple[PaperMarketDataSnapshot, ...]:
        if not instrument_id.strip():
            raise ValueError("instrument_id must not be blank")
        if source_id == "":
            raise ValueError("source_id must not be blank")
        values = tuple(
            snapshot
            for (stored_instrument, stored_source, _), snapshot in self._snapshots.items()
            if stored_instrument == instrument_id
            and (source_id is None or stored_source == source_id)
        )
        return tuple(
            sorted(values, key=lambda item: (item.observed_at, item.source_id))
        )
