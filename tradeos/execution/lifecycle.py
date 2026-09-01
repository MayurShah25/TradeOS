"""Deterministic execution lifecycle and reconciliation primitives."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from .models import OrderStatus


class ExecutionEventType(StrEnum):
    """Normalized execution events emitted by an execution adapter."""

    ACCEPTED = "ACCEPTED"
    FILLED = "FILLED"
    REJECTED = "REJECTED"


@dataclass(frozen=True, slots=True)
class ExecutionEvent:
    """Immutable execution event used for audit and reconciliation."""

    order_id: str
    status: OrderStatus
    event_type: ExecutionEventType
    timestamp: datetime
    filled_quantity: Decimal = Decimal(0)

    def validate(self) -> None:
        """Validate event invariants before persistence or reconciliation."""
        if not self.order_id:
            raise ValueError("order_id must not be empty")
        if self.filled_quantity < 0:
            raise ValueError("filled_quantity must not be negative")
        if self.status is OrderStatus.FILLED and self.filled_quantity <= 0:
            raise ValueError("filled order must have positive filled_quantity")


@dataclass(frozen=True, slots=True)
class ReconciliationResult:
    """Result of comparing expected and observed execution state."""

    order_id: str
    expected_status: OrderStatus
    observed_status: OrderStatus | None

    @property
    def matched(self) -> bool:
        """Return whether expected and observed states agree."""
        return self.expected_status is self.observed_status


class ExecutionReconciler:
    """Compare canonical expected order state with broker-observed state."""

    @staticmethod
    def reconcile(
        order_id: str,
        expected_status: OrderStatus,
        observed_status: OrderStatus | None,
    ) -> ReconciliationResult:
        if not order_id:
            raise ValueError("order_id must not be empty")
        return ReconciliationResult(
            order_id=order_id,
            expected_status=expected_status,
            observed_status=observed_status,
        )
