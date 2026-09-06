"""Deterministic walk-forward validation primitives for TradeOS Phase 4."""

from dataclasses import dataclass

from tradeos.backtest.engine import BacktestEngine
from tradeos.backtest.types import BacktestRequest, BacktestResult
from tradeos.strategy.strategies import Strategy


@dataclass(frozen=True, slots=True)
class WalkForwardRequest:
    """Immutable configuration for expanding-window walk-forward validation."""

    warmup_bars: int
    test_bars: int
    step_bars: int

    def __post_init__(self) -> None:
        if self.warmup_bars < 1:
            raise ValueError("warmup_bars must be at least 1")
        if self.test_bars < 1:
            raise ValueError("test_bars must be at least 1")
        if self.step_bars < 1:
            raise ValueError("step_bars must be at least 1")


@dataclass(frozen=True, slots=True)
class WalkForwardFold:
    """Immutable out-of-sample fold boundaries and result."""

    fold_index: int
    train_end_index: int
    test_start_index: int
    test_end_index: int
    result: BacktestResult


class WalkForwardValidator:
    """Run deterministic expanding-window out-of-sample backtests."""

    def __init__(self, engine: BacktestEngine | None = None) -> None:
        self._engine = engine or BacktestEngine()

    def run(
        self,
        request: BacktestRequest,
        strategy: Strategy,
        validation: WalkForwardRequest,
    ) -> tuple[WalkForwardFold, ...]:
        """Validate a strategy across sequential, non-overlapping test windows."""
        bars = request.bars
        first_test_start = validation.warmup_bars
        if first_test_start >= len(bars):
            raise ValueError("not enough bars for the requested walk-forward warmup")

        folds: list[WalkForwardFold] = []
        test_start = first_test_start
        fold_index = 0
        while test_start < len(bars):
            test_end = min(test_start + validation.test_bars, len(bars))
            fold_request = BacktestRequest(
                bars[:test_end],
                request.initial_capital,
                request.cost_model,
            )
            result = self._engine.run(fold_request, strategy, start_index=test_start)
            folds.append(
                WalkForwardFold(
                    fold_index,
                    test_start - 1,
                    test_start,
                    test_end,
                    result,
                )
            )
            fold_index += 1
            test_start += validation.step_bars

        return tuple(folds)
