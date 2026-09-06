"""Deterministic backtesting primitives for TradeOS Phase 4."""

from .analytics import BacktestMetrics, calculate_metrics
from .engine import BacktestEngine
from .robustness import RobustnessAnalyzer, RobustnessResult, RobustnessScenario
from .types import BacktestRequest, BacktestResult, BacktestTrade, ExecutionCostModel
from .walk_forward import WalkForwardFold, WalkForwardRequest, WalkForwardValidator
from .walk_forward_analytics import WalkForwardMetrics, calculate_walk_forward_metrics
from .walk_forward_validation import (
    WalkForwardValidationConfig,
    WalkForwardValidationResult,
    evaluate_walk_forward_gate,
)

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
    "WalkForwardMetrics",
    "WalkForwardRequest",
    "WalkForwardValidationConfig",
    "WalkForwardValidationResult",
    "WalkForwardValidator",
    "calculate_metrics",
    "calculate_walk_forward_metrics",
    "evaluate_walk_forward_gate",
]
