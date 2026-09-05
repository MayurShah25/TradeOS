"""Deterministic backtesting primitives for TradeOS Phase 4."""

from .analytics import BacktestMetrics, calculate_metrics
from .engine import BacktestEngine
from .types import BacktestRequest, BacktestResult, BacktestTrade

__all__ = [
    "BacktestEngine",
    "BacktestMetrics",
    "BacktestRequest",
    "BacktestResult",
    "BacktestTrade",
    "calculate_metrics",
]
