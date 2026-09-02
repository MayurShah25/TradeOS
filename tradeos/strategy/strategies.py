"""Strategy contracts for TradeOS Phase 4."""

from collections.abc import Sequence
from typing import Protocol

from tradeos.strategy.types import HistoricalBar, Signal


class Strategy(Protocol):
    """Deterministic contract for a strategy implementation."""

    strategy_id: str
    version: str

    def signal(self, history: Sequence[HistoricalBar]) -> Signal:
        """Return a signal from the supplied historical bars."""
