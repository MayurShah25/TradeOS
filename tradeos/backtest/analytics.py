"""Deterministic backtest performance metrics for TradeOS Phase 4."""

from dataclasses import dataclass

from tradeos.backtest.types import BacktestResult


@dataclass(frozen=True, slots=True)
class BacktestMetrics:
    """Immutable performance summary derived from realized backtest trades."""

    trade_count: int
    winning_trades: int
    losing_trades: int
    gross_profit: float
    gross_loss: float
    realized_pnl: float
    total_return: float
    win_rate: float
    profit_factor: float
    average_trade_pnl: float
    equity_curve: tuple[float, ...]
    drawdown_curve: tuple[float, ...]
    max_drawdown: float


def calculate_metrics(result: BacktestResult) -> BacktestMetrics:
    """Calculate deterministic performance metrics from a backtest result."""
    pnls = tuple(trade.net_pnl for trade in result.trades)
    trade_count = len(pnls)
    winning_trades = sum(pnl > 0 for pnl in pnls)
    losing_trades = sum(pnl < 0 for pnl in pnls)
    gross_profit = sum(pnl for pnl in pnls if pnl > 0)
    gross_loss = sum(-pnl for pnl in pnls if pnl < 0)
    realized_pnl = sum(pnls)
    total_return = realized_pnl / result.initial_capital
    win_rate = winning_trades / trade_count if trade_count else 0.0
    profit_factor = (
        gross_profit / gross_loss if gross_loss else float("inf") if gross_profit else 0.0
    )
    average_trade_pnl = realized_pnl / trade_count if trade_count else 0.0

    equity = result.initial_capital
    peak_equity = equity
    equity_curve = [equity]
    drawdown_curve = [0.0]
    max_drawdown = 0.0
    for pnl in pnls:
        equity += pnl
        peak_equity = max(peak_equity, equity)
        drawdown = peak_equity - equity
        max_drawdown = max(max_drawdown, drawdown)
        equity_curve.append(equity)
        drawdown_curve.append(drawdown)

    return BacktestMetrics(
        trade_count=trade_count,
        winning_trades=winning_trades,
        losing_trades=losing_trades,
        gross_profit=gross_profit,
        gross_loss=gross_loss,
        realized_pnl=realized_pnl,
        total_return=total_return,
        win_rate=win_rate,
        profit_factor=profit_factor,
        average_trade_pnl=average_trade_pnl,
        equity_curve=tuple(equity_curve),
        drawdown_curve=tuple(drawdown_curve),
        max_drawdown=max_drawdown,
    )
