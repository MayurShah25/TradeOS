from decimal import Decimal

import pytest

from tradeos.execution import Order, OrderSide, OrderStatus, PaperBroker


def make_order(order_id: str = "order-1") -> Order:
    return Order(
        order_id=order_id,
        instrument_id="US-EQUITY:AAPL",
        side=OrderSide.BUY,
        quantity=Decimal(10),
    )


def test_paper_broker_fills_valid_order() -> None:
    broker = PaperBroker()

    assert broker.submit(make_order()) is OrderStatus.FILLED
    assert broker.status("order-1") is OrderStatus.FILLED


def test_paper_broker_is_idempotent() -> None:
    broker = PaperBroker()
    order = make_order()

    first = broker.submit(order)
    second = broker.submit(order)

    assert first is OrderStatus.FILLED
    assert second is OrderStatus.FILLED


def test_order_rejects_non_positive_quantity() -> None:
    order = Order(
        order_id="order-invalid",
        instrument_id="US-EQUITY:AAPL",
        side=OrderSide.BUY,
        quantity=Decimal(0),
    )

    with pytest.raises(ValueError, match="quantity must be greater than zero"):
        PaperBroker().submit(order)
