from decimal import Decimal

import pytest

from tradeos.execution import Order, OrderSide, OrderStatus
from tradeos.portfolio.open_orders import OpenOrder, OpenOrderLedger


def make_order(order_id: str = "o1", side: OrderSide = OrderSide.BUY) -> Order:
    return Order(order_id, "AAPL", side, Decimal(10))


def test_open_order_requires_accepted_status() -> None:
    with pytest.raises(ValueError, match="ACCEPTED"):
        OpenOrder(make_order(), OrderStatus.FILLED).validate()


def test_ledger_adds_and_removes_orders() -> None:
    ledger = OpenOrderLedger()
    order = OpenOrder(make_order(), OrderStatus.ACCEPTED)
    ledger.add(order)
    assert ledger.get("o1") == order
    assert ledger.remove("o1") == order
    assert ledger.orders() == ()


def test_ledger_rejects_duplicate_order_id() -> None:
    ledger = OpenOrderLedger()
    ledger.add(OpenOrder(make_order(), OrderStatus.ACCEPTED))
    with pytest.raises(ValueError, match="already exists"):
        ledger.add(OpenOrder(make_order(), OrderStatus.ACCEPTED))


def test_quantity_by_instrument_is_signed() -> None:
    ledger = OpenOrderLedger()
    ledger.add(OpenOrder(make_order("buy", OrderSide.BUY), OrderStatus.ACCEPTED))
    ledger.add(OpenOrder(make_order("sell", OrderSide.SELL), OrderStatus.ACCEPTED))
    assert ledger.quantity_by_instrument() == {"AAPL": Decimal(0)}
