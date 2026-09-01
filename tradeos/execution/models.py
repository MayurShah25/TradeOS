"""Canonical order models for paper execution."""

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class OrderSide(StrEnum):
    """Order direction."""

    BUY = "BUY"
    SELL = "SELL"


class OrderType(StrEnum):
    """Supported paper order types."""

    MARKET = "MARKET"


class OrderStatus(StrEnum):
    """Normalized order lifecycle state."""

    ACCEPTED = "ACCEPTED"
    FILLED = "FILLED"
    REJECTED = "REJECTED"


@dataclass(frozen=True, slots=True)
class Order:
    """Immutable canonical order request."""

    order_id: str
    instrument_id: str
    side: OrderSide
    quantity: Decimal
    order_type: OrderType = OrderType.MARKET

    def validate(self) -> None:
        """Enforce deterministic order invariants."""
        if not self.order_id:
            raise ValueError("order_id must not be empty")
        if not self.instrument_id:
            raise ValueError("instrument_id must not be empty")
        if self.quantity <= 0:
            raise ValueError("quantity must be greater than zero")
