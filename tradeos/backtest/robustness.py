"""Deterministic robustness analysis for TradeOS Phase 4 backtests."""

from dataclasses import dataclass

from tradeos.backtest.engine import BacktestEngine
from tradeos.backtest.types import BacktestRequest, BacktestResult, ExecutionCostModel
from tradeos.strategy.strategies import Strategy


@dataclass(frozen=True, slots=True)
class RobustnessScenario:
    """Immutable execution-cost scenario for robustness testing."""

    name: str
    cost_model: ExecutionCostModel

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("scenario name must not be blank")


@dataclass(frozen=True, slots=True)
class RobustnessResult:
    """Immutable backtest result associated with one robustness scenario."""

    scenario: RobustnessScenario
    result: BacktestResult


class RobustnessAnalyzer:
    """Run deterministic backtests across explicit execution-cost scenarios."""

    def __init__(self, engine: BacktestEngine | None = None) -> None:
        self._engine = engine or BacktestEngine()

    def run(
        self,
        request: BacktestRequest,
        strategy: Strategy,
        scenarios: tuple[RobustnessScenario, ...],
    ) -> tuple[RobustnessResult, ...]:
        """Run the same strategy and data under each explicit cost scenario."""
        if not scenarios:
            raise ValueError("at least one robustness scenario is required")

        names = tuple(scenario.name for scenario in scenarios)
        if len(names) != len(set(names)):
            raise ValueError("robustness scenario names must be unique")

        return tuple(
            RobustnessResult(
                scenario,
                self._engine.run(
                    BacktestRequest(
                        request.bars,
                        request.initial_capital,
                        scenario.cost_model,
                    ),
                    strategy,
                ),
            )
            for scenario in scenarios
        )
