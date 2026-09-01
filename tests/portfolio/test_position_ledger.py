from decimal import Decimal

import pytest

from tradeos.execution import OrderSide
from tradeos.portfolio import PositionLedger


def test_buy_creates_position() -> None:
    ledger = PositionLedger()

    position = ledger.apply_fill("AAPL", OrderSide.BUY, Decimal(10), Decimal(100))

    assert position.quantity == Decimal(10)
    assert position.average_price == Decimal(100)
    assert position.realized_pnl == Decimal(0)


def test_multiple_buys_use_weighted_average_price() -> None:
    ledger = PositionLedger()
    ledger.apply_fill("AAPL", OrderSide.BUY, Decimal(10), Decimal(100))

    position = ledger.apply_fill("AAPL", OrderSide.BUY, Decimal(10), Decimal(120))

    assert position.quantity == Decimal(20)
    assert position.average_price == Decimal(110)


def test_partial_sell_realizes_pnl() -> None:
    ledger = PositionLedger()
    ledger.apply_fill("AAPL", OrderSide.BUY, Decimal(10), Decimal(100))

    position = ledger.apply_fill("AAPL", OrderSide.SELL, Decimal(4), Decimal(120))

    assert position.quantity == Decimal(6)
    assert position.average_price == Decimal(100)
    assert position.realized_pnl == Decimal(80)


def test_reversal_starts_new_position_at_fill_price() -> None:
    ledger = PositionLedger()
    ledger.apply_fill("AAPL", OrderSide.BUY, Decimal(10), Decimal(100))

    position = ledger.apply_fill("AAPL", OrderSide.SELL, Decimal(15), Decimal(120))

    assert position.quantity == Decimal(-5)
    assert position.average_price == Decimal(120)
    assert position.realized_pnl == Decimal(200)


def test_position_can_be_closed() -> None:
    ledger = PositionLedger()
    ledger.apply_fill("AAPL", OrderSide.BUY, Decimal(10), Decimal(100))

    position = ledger.apply_fill("AAPL", OrderSide.SELL, Decimal(10), Decimal(90))

    assert position.quantity == Decimal(0)
    assert position.average_price == Decimal(0)
    assert position.realized_pnl == Decimal(-100)


@pytest.mark.parametrize(
    ("quantity", "price"),
    [(Decimal(0), Decimal(100)), (Decimal(-1), Decimal(100)), (Decimal(1), Decimal(0))],
)
def test_invalid_fill_values_are_rejected(quantity: Decimal, price: Decimal) -> None:
    ledger = PositionLedger()

    with pytest.raises(ValueError):
        ledger.apply_fill("AAPL", OrderSide.BUY, quantity, price)
