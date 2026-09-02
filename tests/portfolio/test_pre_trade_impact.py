from decimal import Decimal

from tradeos.execution import Order, OrderSide
from tradeos.portfolio.open_orders import OpenOrderLedger
from tradeos.portfolio.position_ledger import PositionLedger
from tradeos.portfolio.pre_trade_impact import PreTradeImpactCalculator


def test_pre_trade_impact_projects_new_order() -> None:
    impact = PreTradeImpactCalculator.calculate(
        PositionLedger(),
        OpenOrderLedger(),
        {"AAPL": Decimal(100)},
        Decimal(10000),
        Order("o1", "AAPL", OrderSide.BUY, Decimal(10)),
    )
    assert impact.current_exposure.gross == Decimal(0)
    assert impact.projected_exposure.gross == Decimal(1000)
    assert impact.exposure_change == Decimal(1000)
    assert impact.heat_change == Decimal("0.1")
