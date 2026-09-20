"""Deterministic backtest contracts for TradeOS Phase 4."""

from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from typing import NamedTuple

from tradeos.strategy import HistoricalBar


@dataclass(frozen=True, slots=True)
class ExecutionCostModel:
    """Immutable commission and slippage assumptions for historical simulation."""

    commission_per_order: float = 0.0
    slippage_bps: float = 0.0

    def __post_init__(self) -> None:
        if not isfinite(self.commission_per_order) or self.commission_per_order < 0:
            raise ValueError("commission_per_order must be finite and non-negative")
        if not isfinite(self.slippage_bps) or not 0 <= self.slippage_bps <= 10_000:
            raise ValueError("slippage_bps must be between 0 and 10000")

    def buy_price(self, raw_price: float) -> float:
        """Return the effective buy price after adverse slippage."""
        return raw_price * (1 + self.slippage_bps / 10_000)

    def sell_price(self, raw_price: float) -> float:
        """Return the effective sell price after adverse slippage."""
        return raw_price * (1 - self.slippage_bps / 10_000)


@dataclass(frozen=True, slots=True)
class BacktestRequest:
    """Immutable input for a deterministic historical backtest."""

    bars: tuple[HistoricalBar, ...]
    initial_capital: float = 100_000.0
    cost_model: ExecutionCostModel = ExecutionCostModel()

    def __post_init__(self) -> None:
        if self.initial_capital <= 0:
            raise ValueError("initial_capital must be greater than zero")


class BacktestTrade(NamedTuple):
    """A simulated long trade with raw prices and realized execution costs."""

    entry_timestamp: datetime
    entry_price: float
    exit_timestamp: datetime
    exit_price: float
    entry_slippage: float = 0.0
    exit_slippage: float = 0.0
    commission: float = 0.0

    @property
    def effective_entry_price(self) -> float:
        """Return the entry price after slippage."""
        return self.entry_price + self.entry_slippage

    @property
    def effective_exit_price(self) -> float:
        """Return the exit price after slippage."""
        return self.exit_price + self.exit_slippage

    @property
    def net_pnl(self) -> float:
        """Return realized P&L after slippage and commission."""
        return self.effective_exit_price - self.effective_entry_price - self.commission


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
