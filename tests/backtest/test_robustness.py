"""Tests for deterministic Phase 4 robustness analysis."""

from datetime import UTC, datetime

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
        HistoricalBar(datetime(2026, 1, index, tzinfo=UTC), price, price, price, price, 100.0)
        for index, price in enumerate((10.0, 10.0, 12.0))
    )


def test_robustness_analyzer_runs_each_explicit_scenario() -> None:
    request = BacktestRequest(bars(), initial_capital=100.0)
    scenarios = (
        RobustnessScenario("baseline", ExecutionCostModel()),
        RobustnessScenario("stress", ExecutionCostModel(commission_per_order=0.5, slippage_bps=100)),
    )

    results = RobustnessAnalyzer().run(request, FixedSignalStrategy(), scenarios)

    assert tuple(item.scenario.name for item in results) == ("baseline", "stress")
    assert results[0].result.trades[0].net_pnl == 2.0
    assert results[1].result.trades[0].net_pnl == -0.2


def test_robustness_analyzer_preserves_strategy_and_data() -> None:
    request = BacktestRequest(bars(), initial_capital=250.0)
    scenario = RobustnessScenario("baseline", ExecutionCostModel())

    result = RobustnessAnalyzer().run(request, FixedSignalStrategy(), (scenario,))[0]

    assert result.result.strategy_id == "fixed-signal"
    assert result.result.strategy_version == "1.0.0"
    assert result.result.initial_capital == 250.0
    assert result.result.trades[0].entry_price == 10.0
    assert result.result.trades[0].exit_price == 12.0
