"""Tests for building validation evidence from research results."""

from datetime import UTC, datetime

import pytest

from tradeos.backtest import (
    BacktestEngine,
    BacktestRequest,
    ExecutionCostModel,
    RobustnessAnalyzer,
    RobustnessScenario,
    WalkForwardValidationConfig,
    calculate_metrics,
    calculate_walk_forward_metrics,
    evaluate_walk_forward_gate,
)
from tradeos.backtest.walk_forward import WalkForwardRequest, WalkForwardValidator
from tradeos.strategy import HistoricalBar, Signal
from tradeos.validation import ValidationStage
from tradeos.validation.builders import (
    BacktestValidationConfig,
    OutOfSampleValidationConfig,
    RobustnessValidationConfig,
    build_validation_evidence,
    evaluate_out_of_sample_gate,
)


class FixedSignalStrategy:
    """Deterministic strategy fixture for validation evidence tests."""

    strategy_id = "validation-fixture"
    version = "1.0.0"

    def signal(self, history: list[HistoricalBar]) -> Signal:
        """Produce one profitable round trip from prior bars."""
        if len(history) == 3:
            return Signal.BUY
        if len(history) == 4:
            return Signal.SELL
        return Signal.HOLD


def bars() -> tuple[HistoricalBar, ...]:
    """Build deterministic data with two out-of-sample folds."""
    start = datetime(2026, 1, 1, tzinfo=UTC)
    prices = (10.0, 10.0, 10.0, 10.0, 12.0, 12.0, 12.0)
    return tuple(
        HistoricalBar(
            start.replace(day=start.day + index),
            price,
            price,
            price,
            price,
            100.0,
        )
        for index, price in enumerate(prices)
    )


def build_results() -> tuple:
    """Build real Phase 4 outputs used by the evidence builder."""
    strategy = FixedSignalStrategy()
    request = BacktestRequest(bars(), initial_capital=100.0)
    backtest = BacktestEngine().run(request, strategy)
    robustness = RobustnessAnalyzer().run(
        request,
        strategy,
        (
            RobustnessScenario("baseline", ExecutionCostModel()),
            RobustnessScenario("stress", ExecutionCostModel(commission_per_order=0.1)),
        ),
    )
    validation = WalkForwardRequest(warmup_bars=3, test_bars=2, step_bars=2)
    folds = WalkForwardValidator().run(request, strategy, validation)
    walk_metrics = calculate_walk_forward_metrics(folds)
    walk_gate = evaluate_walk_forward_gate(
        walk_metrics,
        WalkForwardValidationConfig(min_fold_count=2, min_total_return=0.0),
    )
    return calculate_metrics(backtest), robustness, walk_metrics, walk_gate


def test_builder_uses_actual_research_results() -> None:
    metrics, robustness, walk_metrics, walk_gate = build_results()

    evidence = build_validation_evidence(
        evidence_id="evidence-1",
        dataset_version="dataset-2026-01",
        configuration_version="config-1",
        code_version="commit-1",
        generated_at=datetime(2026, 1, 1, tzinfo=UTC),
        strategy_id="validation-fixture",
        strategy_version="1.0.0",
        backtest_metrics=metrics,
        backtest_config=BacktestValidationConfig(min_trade_count=1),
        robustness_results=robustness,
        robustness_config=RobustnessValidationConfig(min_total_return=0.0),
        walk_forward_metrics=walk_metrics,
        walk_forward_gate=walk_gate,
        out_of_sample_config=OutOfSampleValidationConfig(min_fold_count=2, min_fold_return=0.0),
    )

    assert evidence.result_for(ValidationStage.BACKTEST) is True
    assert evidence.result_for(ValidationStage.ROBUSTNESS) is True
    assert evidence.result_for(ValidationStage.OUT_OF_SAMPLE) is True
    assert evidence.result_for(ValidationStage.WALK_FORWARD) is True
    assert evidence.known_limitations == ()


def test_failed_result_is_preserved_as_limitation() -> None:
    metrics, robustness, walk_metrics, walk_gate = build_results()

    evidence = build_validation_evidence(
        evidence_id="evidence-2",
        dataset_version="dataset-2026-01",
        configuration_version="config-1",
        code_version="commit-1",
        generated_at=datetime(2026, 1, 1, tzinfo=UTC),
        strategy_id="validation-fixture",
        strategy_version="1.0.0",
        backtest_metrics=metrics,
        backtest_config=BacktestValidationConfig(min_trade_count=99),
        robustness_results=robustness,
        robustness_config=RobustnessValidationConfig(min_total_return=0.0),
        walk_forward_metrics=walk_metrics,
        walk_forward_gate=walk_gate,
        out_of_sample_config=OutOfSampleValidationConfig(min_fold_count=2, min_fold_return=0.0),
    )

    assert evidence.result_for(ValidationStage.BACKTEST) is False
    assert any("trade_count" in item for item in evidence.known_limitations)


def test_oos_gate_requires_matching_fold_results() -> None:
    metrics, _, _, _ = build_results()

    with pytest.raises(ValueError, match="fold_returns"):
        evaluate_out_of_sample_gate(
            metrics,
            metrics.fold_returns[:-1],
            OutOfSampleValidationConfig(),
        )
