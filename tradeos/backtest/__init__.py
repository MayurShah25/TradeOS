"""Deterministic backtesting primitives for TradeOS Phase 4."""

from .analytics import BacktestMetrics, calculate_metrics
from .engine import BacktestEngine
from .robustness import RobustnessAnalyzer, RobustnessResult, RobustnessScenario
from .types import BacktestRequest, BacktestResult, BacktestTrade, ExecutionCostModel
from .walk_forward import WalkForwardFold, WalkForwardRequest, WalkForwardValidator

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
    "WalkForwardFold",
    "WalkForwardRequest",
    "WalkForwardValidator",
    "calculate_metrics",
]
