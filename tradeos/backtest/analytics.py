"""Deterministic backtest performance metrics for TradeOS Phase 4."""

from dataclasses import dataclass

from tradeos.backtest.types import BacktestResult


@dataclass(frozen=True, slots=True)
class BacktestMetrics:
    """Immutable performance summary derived from realized backtest trades."""

    trade_count: int
    winning_trades: int
    losing_trades: int
    realized_pnl: float
    total_return: float
    win_rate: float
    max_drawdown: float


def calculate_metrics(result: BacktestResult) -> BacktestMetrics:
    """Calculate deterministic performance metrics from a backtest result."""
    pnls = tuple(trade.net_pnl for trade in result.trades)
    trade_count = len(pnls)
    winning_trades = sum(pnl > 0 for pnl in pnls)
    losing_trades = sum(pnl < 0 for pnl in pnls)
    realized_pnl = sum(pnls)
    total_return = realized_pnl / result.initial_capital
    win_rate = winning_trades / trade_count if trade_count else 0.0

    equity = result.initial_capital
    peak_equity = equity
    max_drawdown = 0.0
    for pnl in pnls:
        equity += pnl
        peak_equity = max(peak_equity, equity)
        max_drawdown = max(max_drawdown, peak_equity - equity)

    return BacktestMetrics(
        trade_count=trade_count,
        winning_trades=winning_trades,
        losing_trades=losing_trades,
        realized_pnl=realized_pnl,
        total_return=total_return,
        win_rate=win_rate,
        max_drawdown=max_drawdown,
    )
