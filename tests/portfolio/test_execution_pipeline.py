from datetime import UTC, datetime
from decimal import Decimal

import pytest

from tradeos.execution import Order, OrderSide, OrderStatus
from tradeos.execution.lifecycle import ExecutionEvent, ExecutionEventType
from tradeos.portfolio import ExecutionPortfolioPipeline

TIMESTAMP = datetime(2026, 1, 1, tzinfo=UTC)


def order() -> Order:
    return Order("order-1", "AAPL", OrderSide.BUY, Decimal(10))


def event(status: OrderStatus, quantity: Decimal = Decimal(0)) -> ExecutionEvent:
    return ExecutionEvent(
        order_id="order-1",
        status=status,
        event_type=ExecutionEventType(status.value),
        timestamp=TIMESTAMP,
        filled_quantity=quantity,
    )


def test_accepted_order_reconciles_without_position_change() -> None:
    pipeline = ExecutionPortfolioPipeline()

    result = pipeline.process(
        order(), None, event(OrderStatus.ACCEPTED), OrderStatus.ACCEPTED
    )

    assert result.status is OrderStatus.ACCEPTED
    assert result.reconciled is True
    assert result.portfolio.position_for("AAPL") is None
    assert result.portfolio.realized_pnl == Decimal(0)


def test_filled_order_updates_position_after_reconciliation() -> None:
    pipeline = ExecutionPortfolioPipeline()
    pipeline.process(order(), None, event(OrderStatus.ACCEPTED), OrderStatus.ACCEPTED)

    result = pipeline.process(
        order(),
        OrderStatus.ACCEPTED,
        event(OrderStatus.FILLED, Decimal(10)),
        OrderStatus.FILLED,
        Decimal(100),
    )

    position = result.portfolio.position_for("AAPL")
    assert position is not None
    assert position.quantity == Decimal(10)
    assert position.average_price == Decimal(100)
    assert result.portfolio.realized_pnl == Decimal(0)


def test_rejected_order_does_not_create_position() -> None:
    pipeline = ExecutionPortfolioPipeline()

    result = pipeline.process(
        order(), None, event(OrderStatus.REJECTED), OrderStatus.REJECTED
    )

    assert result.status is OrderStatus.REJECTED
    assert result.portfolio.position_for("AAPL") is None


def test_reconciliation_mismatch_blocks_position_mutation() -> None:
    pipeline = ExecutionPortfolioPipeline()

    with pytest.raises(ValueError, match="reconciliation mismatch"):
        pipeline.process(
            order(),
            None,
            event(OrderStatus.ACCEPTED),
            OrderStatus.REJECTED,
        )

    assert pipeline.ledger.get("AAPL") is None


def test_filled_execution_requires_fill_price() -> None:
    pipeline = ExecutionPortfolioPipeline()
    pipeline.process(order(), None, event(OrderStatus.ACCEPTED), OrderStatus.ACCEPTED)

    with pytest.raises(ValueError, match="fill_price"):
        pipeline.process(
            order(),
            OrderStatus.ACCEPTED,
            event(OrderStatus.FILLED, Decimal(10)),
            OrderStatus.FILLED,
        )


def test_event_for_different_order_is_rejected() -> None:
    pipeline = ExecutionPortfolioPipeline()
    different = ExecutionEvent(
        order_id="other-order",
        status=OrderStatus.ACCEPTED,
        event_type=ExecutionEventType.ACCEPTED,
        timestamp=TIMESTAMP,
    )

    with pytest.raises(ValueError, match="order_id"):
        pipeline.process(order(), None, different, OrderStatus.ACCEPTED)
