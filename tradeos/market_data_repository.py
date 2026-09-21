"""Persistence port for immutable paper market-data snapshots."""

from abc import ABC, abstractmethod
from datetime import datetime

from tradeos.market_data import PaperMarketDataSnapshot


class PaperMarketDataRepository(ABC):
    """Persistence boundary for validated, immutable market-data snapshots."""

    @abstractmethod
    def save(self, snapshot: PaperMarketDataSnapshot) -> None:
        """Persist a snapshot, allowing only exact idempotent re-save."""
        raise NotImplementedError

    @abstractmethod
    def get(
        self,
        *,
        instrument_id: str,
        source_id: str,
        observed_at: datetime,
    ) -> PaperMarketDataSnapshot | None:
        """Return one snapshot identified by instrument, source, and observation time."""
        raise NotImplementedError

    @abstractmethod
    def list_for_instrument(
        self,
        *,
        instrument_id: str,
        source_id: str | None = None,
    ) -> tuple[PaperMarketDataSnapshot, ...]:
        """Return snapshots in deterministic observation-time order."""
        raise NotImplementedError
