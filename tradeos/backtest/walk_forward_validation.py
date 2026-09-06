"""Deterministic validation gates for walk-forward research results."""

from dataclasses import dataclass

from tradeos.backtest.walk_forward_analytics import WalkForwardMetrics


@dataclass(frozen=True, slots=True)
class WalkForwardValidationConfig:
    """Immutable thresholds for evaluating walk-forward research evidence."""

    min_fold_count: int = 1
    min_total_return: float = 0.0
    max_drawdown: float = float("inf")
    min_win_rate: float = 0.0
    min_profit_factor: float = 0.0
    min_profitable_fold_ratio: float = 0.0

    def __post_init__(self) -> None:
        if self.min_fold_count < 1:
            raise ValueError("min_fold_count must be at least 1")
        if self.max_drawdown < 0:
            raise ValueError("max_drawdown must be non-negative")
        if not 0.0 <= self.min_win_rate <= 1.0:
            raise ValueError("min_win_rate must be between 0 and 1")
        if self.min_profit_factor < 0:
            raise ValueError("min_profit_factor must be non-negative")
        if not 0.0 <= self.min_profitable_fold_ratio <= 1.0:
            raise ValueError("min_profitable_fold_ratio must be between 0 and 1")


@dataclass(frozen=True, slots=True)
class WalkForwardValidationResult:
    """Immutable result containing a deterministic gate decision and reasons."""

    passed: bool
    failure_reasons: tuple[str, ...]


def evaluate_walk_forward_gate(
    metrics: WalkForwardMetrics,
    config: WalkForwardValidationConfig,
) -> WalkForwardValidationResult:
    """Evaluate walk-forward metrics against explicit research thresholds."""
    failures: list[str] = []
    profitable_fold_ratio = metrics.profitable_fold_count / metrics.fold_count

    if metrics.fold_count < config.min_fold_count:
        failures.append(
            f"fold_count {metrics.fold_count} is below minimum {config.min_fold_count}"
        )
    if metrics.total_return < config.min_total_return:
        failures.append(
            f"total_return {metrics.total_return} is below minimum {config.min_total_return}"
        )
    if metrics.max_drawdown > config.max_drawdown:
        failures.append(
            f"max_drawdown {metrics.max_drawdown} exceeds maximum {config.max_drawdown}"
        )
    if metrics.win_rate < config.min_win_rate:
        failures.append(f"win_rate {metrics.win_rate} is below minimum {config.min_win_rate}")
    if metrics.profit_factor < config.min_profit_factor:
        failures.append(
            f"profit_factor {metrics.profit_factor} is below minimum {config.min_profit_factor}"
        )
    if profitable_fold_ratio < config.min_profitable_fold_ratio:
        failures.append(
            "profitable_fold_ratio "
            f"{profitable_fold_ratio} is below minimum {config.min_profitable_fold_ratio}"
        )

    return WalkForwardValidationResult(not failures, tuple(failures))
