"""Deterministic strategy implementations for TradeOS Phase 4."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from tradeos.strategy.types import HistoricalBar, Signal


class Strategy(Protocol):
    """Deterministic contract for a strategy implementation."""

    strategy_id: str
    version: str

    def signal(self, history: Sequence[HistoricalBar]) -> Signal:
        """Return a signal from the supplied historical bars."""


@dataclass(frozen=True, slots=True)
class MovingAverageCrossStrategy:
    """Generate signals from a short/long simple moving-average crossover."""

    short_window: int = 3
    long_window: int = 5
    strategy_id: str = "moving-average-cross"
    version: str = "1.0.0"

    def __post_init__(self) -> None:
        if self.short_window < 1:
            raise ValueError("short_window must be at least 1")
        if self.long_window <= self.short_window:
            raise ValueError("long_window must be greater than short_window")

    def signal(self, history: Sequence[HistoricalBar]) -> Signal:
        """Return BUY or SELL only when the moving averages actually cross."""
        if len(history) < self.long_window + 1:
            return Signal.HOLD

        closes = [bar.close for bar in history]
        current_short_average = sum(closes[-self.short_window :]) / self.short_window
        current_long_average = sum(closes[-self.long_window :]) / self.long_window
        previous_short_average = (
            sum(closes[-self.short_window - 1 : -1]) / self.short_window
        )
        previous_long_average = sum(closes[-self.long_window - 1 : -1]) / self.long_window

        if previous_short_average <= previous_long_average and current_short_average > current_long_average:
            return Signal.BUY
        if previous_short_average >= previous_long_average and current_short_average < current_long_average:
            return Signal.SELL
        return Signal.HOLD
