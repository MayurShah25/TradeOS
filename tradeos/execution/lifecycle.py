"""Deterministic execution lifecycle and reconciliation primitives."""

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum

from .models import OrderStatus


class ExecutionEventType(StrEnum):
    """Normalized execution events emitted by an execution adapter."""

    ACCEPTED = "ACCEPTED"
    FILLED = "FILLED"
    REJECTED = "REJECTED"


class ReconciliationStatus(StrEnum):
    """Outcome of comparing expected and observed execution state."""

    MATCHED = "MATCHED"
    MISMATCHED = "MISMATCHED"
    UNKNOWN = "UNKNOWN"


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
        if self.timestamp.tzinfo is None or self.timestamp.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware")
        if self.timestamp.tzinfo is not UTC:
            raise ValueError("timestamp must use UTC")
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
    def status(self) -> ReconciliationStatus:
        """Return matched, mismatched, or unknown without conflating absence with failure."""
        if self.observed_status is None:
            return ReconciliationStatus.UNKNOWN
        if self.expected_status is self.observed_status:
            return ReconciliationStatus.MATCHED
        return ReconciliationStatus.MISMATCHED

    @property
    def matched(self) -> bool:
        """Return whether expected and observed states agree."""
        return self.status is ReconciliationStatus.MATCHED


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
