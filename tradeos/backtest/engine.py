"""Deterministic historical backtest engine for TradeOS Phase 4."""

from tradeos.backtest.types import BacktestRequest, BacktestResult, BacktestTrade
from tradeos.strategy import Signal, Strategy


class BacktestEngine:
    """Run a deterministic, long-only strategy simulation."""

    def run(self, request: BacktestRequest, strategy: Strategy) -> BacktestResult:
        """Evaluate strategy signals and simulate entries and exits at bar closes."""
        trades: list[BacktestTrade] = []
        entry_timestamp = None
        entry_price = None
        history = []

        for bar in request.bars:
            history.append(bar)
            signal = strategy.signal(history)

            if signal is Signal.BUY and entry_timestamp is None:
                entry_timestamp = bar.timestamp
                entry_price = bar.close
            elif (
                signal is Signal.SELL
                and entry_timestamp is not None
                and entry_price is not None
            ):
                trades.append(
                    BacktestTrade(
                        entry_timestamp,
                        entry_price,
                        bar.timestamp,
                        bar.close,
                    )
                )
                entry_timestamp = None
                entry_price = None

        return BacktestResult(
            strategy_id=strategy.strategy_id,
            strategy_version=strategy.version,
            trades=tuple(trades),
            open_entry_timestamp=entry_timestamp,
            open_entry_price=entry_price,
        )
