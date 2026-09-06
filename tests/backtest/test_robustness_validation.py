"""Tests for deterministic Phase 4 robustness scenario validation."""

from datetime import UTC, datetime

import pytest

from tradeos.backtest import BacktestRequest, ExecutionCostModel
from tradeos.backtest.robustness import RobustnessAnalyzer, RobustnessScenario
from tradeos.strategy import HistoricalBar, Signal


class FixedSignalStrategy:
    """Small deterministic strategy fixture for robustness tests."""

    strategy_id = "fixed-signal"
    version = "1.0.0"

    def signal(self, history: tuple[HistoricalBar, ...] | list[HistoricalBar]) -> Signal:
        """Buy on the second bar and sell on the third bar."""
        if len(history) == 2:
            return Signal.BUY
        if len(history) == 3:
            return Signal.SELL
        return Signal.HOLD


def bars() -> tuple[HistoricalBar, ...]:
    """Build a minimal deterministic price series."""
    return tuple(
        HistoricalBar(
            datetime(2026, 1, index + 1, tzinfo=UTC), price, price, price, price, 100.0
        )
        for index, price in enumerate((10.0, 10.0, 12.0))
    )


def test_robustness_analyzer_rejects_empty_scenarios() -> None:
    with pytest.raises(ValueError, match="at least one robustness scenario"):
        RobustnessAnalyzer().run(BacktestRequest(bars()), FixedSignalStrategy(), ())


def test_robustness_analyzer_rejects_duplicate_scenario_names() -> None:
    scenarios = (
        RobustnessScenario("baseline", ExecutionCostModel()),
        RobustnessScenario("baseline", ExecutionCostModel(slippage_bps=100)),
    )

    with pytest.raises(ValueError, match="unique"):
        RobustnessAnalyzer().run(BacktestRequest(bars()), FixedSignalStrategy(), scenarios)


def test_robustness_scenario_rejects_blank_name() -> None:
    with pytest.raises(ValueError, match="name"):
        RobustnessScenario("", ExecutionCostModel())
