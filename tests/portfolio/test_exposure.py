from decimal import Decimal

import pytest

from tradeos.execution import Order, OrderSide, OrderStatus
from tradeos.portfolio.exposure import ExposureCalculator
from tradeos.portfolio.open_orders import OpenOrder, OpenOrderLedger
from tradeos.portfolio.position_ledger import PositionLedger


def test_exposure_includes_positions() -> None:
    ledger = PositionLedger()
    ledger.apply_fill("AAPL", OrderSide.BUY, Decimal(10), Decimal(100))
    exposure = ExposureCalculator.from_positions(ledger, {"AAPL": Decimal(110)})
    assert exposure.gross == Decimal(1100)
    assert exposure.net == Decimal(1100)


def test_exposure_includes_pending_orders() -> None:
    positions = PositionLedger()
    orders = OpenOrderLedger()
    orders.add(OpenOrder(Order("o1", "AAPL", OrderSide.BUY, Decimal(5)), OrderStatus.ACCEPTED))
    exposure = ExposureCalculator.from_positions(positions, {"AAPL": Decimal(100)}, orders)
    assert exposure.gross == Decimal(500)
    assert exposure.net == Decimal(500)


def test_missing_price_is_rejected() -> None:
    ledger = PositionLedger()
    ledger.apply_fill("AAPL", OrderSide.BUY, Decimal(1), Decimal(100))
    with pytest.raises(ValueError, match="missing price"):
        ExposureCalculator.from_positions(ledger, {})


def test_short_position_has_negative_net_exposure() -> None:
    ledger = PositionLedger()
    ledger.apply_fill("AAPL", OrderSide.SELL, Decimal(2), Decimal(100))
    exposure = ExposureCalculator.from_positions(ledger, {"AAPL": Decimal(90)})
    assert exposure.gross == Decimal(180)
    assert exposure.net == Decimal(-180)
