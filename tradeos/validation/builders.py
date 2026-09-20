"""Build immutable validation evidence from deterministic research results."""

from dataclasses import dataclass
from datetime import datetime
from math import isfinite

from tradeos.backtest import (
    BacktestMetrics,
    RobustnessResult,
    WalkForwardMetrics,
    WalkForwardValidationResult,
)
from tradeos.validation.evidence import (
    ValidationEvidence,
    ValidationStage,
)


@dataclass(frozen=True, slots=True)
class BacktestValidationConfig:
    """Thresholds for converting backtest metrics into a validation gate."""

    min_trade_count: int = 1
    min_total_return: float = 0.0
    max_drawdown: float = float("inf")

    def __post_init__(self) -> None:
        if self.min_trade_count < 0:
            raise ValueError("min_trade_count must be non-negative")
        if self.max_drawdown < 0 or not (isfinite(self.max_drawdown) or self.max_drawdown == float("inf")):
            raise ValueError("max_drawdown must be finite and non-negative")
        if not isfinite(self.min_total_return):
            raise ValueError("min_total_return must be finite")


@dataclass(frozen=True, slots=True)
class RobustnessValidationConfig:
    """Thresholds applied independently to every robustness scenario."""

    min_total_return: float = 0.0
    max_drawdown: float = float("inf")

    def __post_init__(self) -> None:
        if self.max_drawdown < 0 or not isfinite(self.max_drawdown):
            raise ValueError("max_drawdown must be finite and non-negative")
        if not isfinite(self.min_total_return):
            raise ValueError("min_total_return must be finite")


@dataclass(frozen=True, slots=True)
class OutOfSampleValidationConfig:
    """Thresholds applied to every out-of-sample walk-forward fold."""

    min_fold_count: int = 1
    min_fold_return: float = 0.0

    def __post_init__(self) -> None:
        if self.min_fold_count < 1:
            raise ValueError("min_fold_count must be at least 1")
        if not isfinite(self.min_fold_return):
            raise ValueError("min_fold_return must be finite")


def evaluate_backtest_gate(
    metrics: BacktestMetrics,
    config: BacktestValidationConfig,
) -> tuple[bool, tuple[str, ...]]:
    """Evaluate one deterministic backtest result against explicit thresholds."""
    failures: list[str] = []
    if metrics.trade_count < config.min_trade_count:
        failures.append(
            f"trade_count {metrics.trade_count} is below minimum {config.min_trade_count}"
        )
    if metrics.total_return < config.min_total_return:
        failures.append(
            f"total_return {metrics.total_return} is below minimum {config.min_total_return}"
        )
    if metrics.max_drawdown > config.max_drawdown:
        failures.append(
            f"max_drawdown {metrics.max_drawdown} exceeds maximum {config.max_drawdown}"
        )
    return not failures, tuple(failures)


def evaluate_robustness_gate(
    results: tuple[RobustnessResult, ...],
    config: RobustnessValidationConfig,
) -> tuple[bool, tuple[str, ...]]:
    """Require every explicit robustness scenario to satisfy the thresholds."""
    if not results:
        raise ValueError("at least one robustness result is required")

    failures: list[str] = []
    for item in results:
        metrics = _metrics_for_result(item)
        if metrics.total_return < config.min_total_return:
            failures.append(
                f"scenario {item.scenario.name}: total_return {metrics.total_return} "
                f"is below minimum {config.min_total_return}"
            )
        if metrics.max_drawdown > config.max_drawdown:
            failures.append(
                f"scenario {item.scenario.name}: max_drawdown {metrics.max_drawdown} "
                f"exceeds maximum {config.max_drawdown}"
            )
    return not failures, tuple(failures)


def evaluate_out_of_sample_gate(
    metrics: WalkForwardMetrics,
    fold_returns: tuple[float, ...],
    config: OutOfSampleValidationConfig,
) -> tuple[bool, tuple[str, ...]]:
    """Require enough out-of-sample folds and a minimum return in every fold."""
    if metrics.fold_count != len(fold_returns):
        raise ValueError("fold_returns must match walk-forward fold_count")

    failures: list[str] = []
    if metrics.fold_count < config.min_fold_count:
        failures.append(
            f"fold_count {metrics.fold_count} is below minimum {config.min_fold_count}"
        )
    for index, fold_return in enumerate(fold_returns):
        if fold_return < config.min_fold_return:
            failures.append(
                f"fold {index} return {fold_return} is below minimum {config.min_fold_return}"
            )
    return not failures, tuple(failures)


def build_validation_evidence(
    *,
    evidence_id: str,
    dataset_version: str,
    configuration_version: str,
    code_version: str,
    generated_at: datetime,
    strategy_id: str,
    strategy_version: str,
    backtest_metrics: BacktestMetrics,
    backtest_config: BacktestValidationConfig,
    robustness_results: tuple[RobustnessResult, ...],
    robustness_config: RobustnessValidationConfig,
    walk_forward_metrics: WalkForwardMetrics,
    walk_forward_gate: WalkForwardValidationResult,
    out_of_sample_config: OutOfSampleValidationConfig,
) -> ValidationEvidence:
    """Create immutable evidence from actual backtest and validation outputs."""
    backtest_passed, backtest_failures = evaluate_backtest_gate(
        backtest_metrics, backtest_config
    )
    robustness_passed, robustness_failures = evaluate_robustness_gate(
        robustness_results, robustness_config
    )
    oos_passed, oos_failures = evaluate_out_of_sample_gate(
        walk_forward_metrics,
        walk_forward_metrics.fold_returns,
        out_of_sample_config,
    )

    limitations = (
        *backtest_failures,
        *robustness_failures,
        *oos_failures,
        *walk_forward_gate.failure_reasons,
    )
    return ValidationEvidence(
        evidence_id=evidence_id,
        strategy_id=strategy_id,
        strategy_version=strategy_version,
        dataset_version=dataset_version,
        configuration_version=configuration_version,
        code_version=code_version,
        generated_at=generated_at,
        gate_results=(
            (ValidationStage.BACKTEST, backtest_passed),
            (ValidationStage.ROBUSTNESS, robustness_passed),
            (ValidationStage.OUT_OF_SAMPLE, oos_passed),
            (ValidationStage.WALK_FORWARD, walk_forward_gate.passed),
        ),
        known_limitations=limitations,
    )


def _metrics_for_result(result: RobustnessResult) -> BacktestMetrics:
    """Calculate metrics for one robustness result without mutating it."""
    from tradeos.backtest.analytics import calculate_metrics

    return calculate_metrics(result.result)
