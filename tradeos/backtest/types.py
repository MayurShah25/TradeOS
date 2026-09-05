"""Deterministic backtest contracts for TradeOS Phase 4."""

from dataclasses import dataclass
from datetime import datetime
from typing import NamedTuple

from tradeos.strategy import HistoricalBar


@dataclass(frozen=True, slots=True)
class BacktestRequest:
    """Immutable input for a deterministic historical backtest."""

    bars: tuple[HistoricalBar, ...]
    initial_capital: float = 100_000.0

    def __post_init__(self) -> None:
        if self.initial_capital <= 0:
            raise ValueError("initial_capital must be greater than zero")


class BacktestTrade(NamedTuple):
    """A simulated long trade opened and closed at historical bar closes."""

    entry_timestamp: datetime
    entry_price: float
    exit_timestamp: datetime
    exit_price: float


@dataclass(frozen=True, slots=True)
class BacktestResult:
    """Immutable output containing simulated trades and final position state."""

    strategy_id: str
    strategy_version: str
    initial_capital: float
    trades: tuple[BacktestTrade, ...]
    open_entry_timestamp: datetime | None
    open_entry_price: float | None

    @property
    def position_open(self) -> bool:
        """Return whether the backtest finished with an open long position."""
        return self.open_entry_timestamp is not None
