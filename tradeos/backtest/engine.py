"""Deterministic historical backtest engine for TradeOS Phase 4."""

from tradeos.backtest.types import BacktestRequest, BacktestResult, BacktestTrade
from tradeos.strategy import Signal, Strategy


class BacktestEngine:
    """Run a deterministic, long-only strategy simulation."""

    def run(
        self,
        request: BacktestRequest,
        strategy: Strategy,
        start_index: int = 0,
    ) -> BacktestResult:
        """Evaluate strategy signals and simulate entries and exits at bar closes."""
        if not 0 <= start_index < len(request.bars) if request.bars else start_index != 0:
            raise ValueError("start_index must reference a bar in the request")

        trades: list[BacktestTrade] = []
        entry_timestamp = None
        entry_price = None
        entry_slippage = 0.0
        history = []

        for index, bar in enumerate(request.bars):
            history.append(bar)
            if index < start_index:
                continue
            signal = strategy.signal(history)

            if signal is Signal.BUY and entry_timestamp is None:
                entry_timestamp = bar.timestamp
                entry_price = bar.close
                entry_slippage = request.cost_model.buy_price(bar.close) - bar.close
            elif signal is Signal.SELL and entry_timestamp is not None and entry_price is not None:
                closed_entry_timestamp = entry_timestamp
                closed_entry_price = entry_price
                exit_slippage = request.cost_model.sell_price(bar.close) - bar.close
                trades.append(
                    BacktestTrade(
                        closed_entry_timestamp,
                        closed_entry_price,
                        bar.timestamp,
                        bar.close,
                        entry_slippage,
                        exit_slippage,
                        request.cost_model.commission_per_order * 2,
                    )
                )
                entry_timestamp = None
                entry_price = None
                entry_slippage = 0.0

        return BacktestResult(
            strategy_id=strategy.strategy_id,
            strategy_version=strategy.version,
            initial_capital=request.initial_capital,
            trades=tuple(trades),
            open_entry_timestamp=entry_timestamp,
            open_entry_price=entry_price,
        )
