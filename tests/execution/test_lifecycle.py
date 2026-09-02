from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from tradeos.execution import OrderStatus
from tradeos.execution.lifecycle import (
    ExecutionEvent,
    ExecutionEventType,
    ExecutionReconciler,
    ReconciliationStatus,
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


def test_unknown_execution_event_is_valid_without_fill() -> None:
    event = ExecutionEvent(
        order_id="order-1",
        status=OrderStatus.UNKNOWN,
        event_type=ExecutionEventType.UNKNOWN,
        timestamp=datetime.now(UTC),
    )

    event.validate()


def test_unknown_execution_event_cannot_claim_a_fill() -> None:
    event = ExecutionEvent(
        order_id="order-1",
        status=OrderStatus.UNKNOWN,
        event_type=ExecutionEventType.UNKNOWN,
        timestamp=datetime.now(UTC),
        filled_quantity=Decimal(1),
    )

    with pytest.raises(ValueError, match="filled_quantity"):
        event.validate()


def test_execution_event_requires_utc_timestamp() -> None:
    event = ExecutionEvent(
        order_id="order-1",
        status=OrderStatus.ACCEPTED,
        event_type=ExecutionEventType.ACCEPTED,
        timestamp=datetime(2026, 9, 2, tzinfo=timezone(timedelta(hours=5, minutes=30))),
    )

    with pytest.raises(ValueError, match="UTC"):
        event.validate()


def test_reconciliation_matches_observed_status() -> None:
    result = ExecutionReconciler.reconcile("order-1", OrderStatus.FILLED, OrderStatus.FILLED)

    assert result.status is ReconciliationStatus.MATCHED
    assert result.matched is True


def test_reconciliation_flags_mismatched_observed_status() -> None:
    result = ExecutionReconciler.reconcile("order-1", OrderStatus.FILLED, OrderStatus.REJECTED)

    assert result.status is ReconciliationStatus.MISMATCHED
    assert result.matched is False


def test_reconciliation_distinguishes_unknown_observed_status() -> None:
    result = ExecutionReconciler.reconcile("order-1", OrderStatus.FILLED, None)

    assert result.status is ReconciliationStatus.UNKNOWN
    assert result.matched is False


def test_reconciliation_treats_explicit_unknown_as_unknown() -> None:
    result = ExecutionReconciler.reconcile("order-1", OrderStatus.FILLED, OrderStatus.UNKNOWN)

    assert result.status is ReconciliationStatus.UNKNOWN
    assert result.matched is False
