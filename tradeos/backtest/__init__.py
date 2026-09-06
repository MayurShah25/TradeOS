"""Deterministic backtesting primitives for TradeOS Phase 4."""

from .analytics import BacktestMetrics, calculate_metrics
from .engine import BacktestEngine
from .robustness import RobustnessAnalyzer, RobustnessResult, RobustnessScenario
from .types import BacktestRequest, BacktestResult, BacktestTrade, ExecutionCostModel

__all__ = [
    "BacktestEngine",
    "BacktestMetrics",
    "BacktestRequest",
    "BacktestResult",
    "BacktestTrade",
    "ExecutionCostModel",
    "RobustnessAnalyzer",
    "RobustnessResult",
    "RobustnessScenario",
    "calculate_metrics",
]
