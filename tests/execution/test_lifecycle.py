from datetime import UTC, datetime
from decimal import Decimal

import pytest

from tradeos.execution import OrderStatus
from tradeos.execution.lifecycle import (
    ExecutionEvent,
    ExecutionEventType,
    ExecutionReconciler,
)


def test_filled_execution_event_requires_positive_fill() -> None:
    event = ExecutionEvent(
        order_id="order-1",
        status=OrderStatus.FILLED,
        event_type=ExecutionEventType.FILLED,
        timestamp=datetime.now(UTC),
    )

    with pytest.raises(ValueError, match="positive filled_quantity"):
        event.validate()


def test_execution_event_accepts_valid_fill() -> None:
    event = ExecutionEvent(
        order_id="order-1",
        status=OrderStatus.FILLED,
        event_type=ExecutionEventType.FILLED,
        timestamp=datetime.now(UTC),
        filled_quantity=Decimal(10),
    )

    event.validate()


def test_reconciliation_matches_observed_status() -> None:
    result = ExecutionReconciler.reconcile(
        "order-1", OrderStatus.FILLED, OrderStatus.FILLED
    )

    assert result.matched is True


def test_reconciliation_flags_missing_observed_status() -> None:
    result = ExecutionReconciler.reconcile("order-1", OrderStatus.FILLED, None)

    assert result.matched is False
