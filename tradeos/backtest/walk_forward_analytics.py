"""Deterministic aggregate metrics for TradeOS walk-forward validation."""

from dataclasses import dataclass

from tradeos.backtest.analytics import BacktestMetrics, calculate_metrics
from tradeos.backtest.walk_forward import WalkForwardFold


@dataclass(frozen=True, slots=True)
class WalkForwardMetrics:
    """Immutable aggregate performance summary across out-of-sample folds."""

    fold_count: int
    profitable_fold_count: int
    losing_fold_count: int
    total_trade_count: int
    realized_pnl: float
    total_return: float
    win_rate: float
    profit_factor: float
    average_trade_pnl: float
    max_drawdown: float
    mean_fold_return: float
    worst_fold_return: float
    fold_returns: tuple[float, ...]


def calculate_walk_forward_metrics(
    folds: tuple[WalkForwardFold, ...],
) -> WalkForwardMetrics:
    """Aggregate deterministic performance metrics across walk-forward folds."""
    if not folds:
        raise ValueError("at least one walk-forward fold is required")

    metrics = tuple(calculate_metrics(fold.result) for fold in folds)
    initial_capital = folds[0].result.initial_capital
    if any(fold.result.initial_capital != initial_capital for fold in folds[1:]):
        raise ValueError("all walk-forward folds must use the same initial capital")

    total_trade_count = sum(item.trade_count for item in metrics)
    realized_pnl = sum(item.realized_pnl for item in metrics)
    gross_profit = sum(item.gross_profit for item in metrics)
    gross_loss = sum(item.gross_loss for item in metrics)
    winning_trades = sum(item.winning_trades for item in metrics)
    profit_factor = gross_profit / gross_loss if gross_loss else float("inf") if gross_profit else 0.0
    average_trade_pnl = realized_pnl / total_trade_count if total_trade_count else 0.0
    fold_returns = tuple(item.total_return for item in metrics)
    profitable_fold_count = sum(item.realized_pnl > 0 for item in metrics)
    losing_fold_count = sum(item.realized_pnl < 0 for item in metrics)

    return WalkForwardMetrics(
        fold_count=len(folds),
        profitable_fold_count=profitable_fold_count,
        losing_fold_count=losing_fold_count,
        total_trade_count=total_trade_count,
        realized_pnl=realized_pnl,
        total_return=realized_pnl / initial_capital,
        win_rate=winning_trades / total_trade_count if total_trade_count else 0.0,
        profit_factor=profit_factor,
        average_trade_pnl=average_trade_pnl,
        max_drawdown=max(item.max_drawdown for item in metrics),
        mean_fold_return=sum(fold_returns) / len(fold_returns),
        worst_fold_return=min(fold_returns),
        fold_returns=fold_returns,
    )
