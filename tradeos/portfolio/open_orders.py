"""Deterministic open-order ledger for portfolio state."""

from dataclasses import dataclass
from decimal import Decimal

from tradeos.execution import Order, OrderSide, OrderStatus


@dataclass(frozen=True, slots=True)
class OpenOrder:
    """Immutable normalized representation of a live order."""

    order: Order
    status: OrderStatus
    limit_price: Decimal | None = None

    def validate(self) -> None:
        """Validate open-order invariants."""
        self.order.validate()
        if self.status is not OrderStatus.ACCEPTED:
            raise ValueError("open order status must be ACCEPTED")
        if self.limit_price is not None and self.limit_price <= 0:
            raise ValueError("limit_price must be positive")


class OpenOrderLedger:
    """Maintain deterministic accepted orders that remain open."""

    def __init__(self) -> None:
        self._orders: dict[str, OpenOrder] = {}

    @classmethod
    def from_orders(cls, orders: tuple[OpenOrder, ...]) -> "OpenOrderLedger":
        """Restore a ledger from an immutable open-order snapshot."""
        ledger = cls()
        for open_order in orders:
            ledger.add(open_order)
        return ledger

    def add(self, open_order: OpenOrder) -> None:
        """Add an accepted order, rejecting duplicate order identifiers."""
        open_order.validate()
        if open_order.order.order_id in self._orders:
            raise ValueError("order_id already exists")
        self._orders[open_order.order.order_id] = open_order

    def remove(self, order_id: str) -> OpenOrder:
        """Remove and return an open order by identifier."""
        try:
            return self._orders.pop(order_id)
        except KeyError as exc:
            raise KeyError(f"unknown open order: {order_id}") from exc

    def get(self, order_id: str) -> OpenOrder | None:
        """Return an open order when present."""
        return self._orders.get(order_id)

    def orders(self) -> tuple[OpenOrder, ...]:
        """Return an immutable snapshot of open orders."""
        return tuple(self._orders.values())

    def quantity_by_instrument(self) -> dict[str, Decimal]:
        """Return signed pending quantity by instrument."""
        quantities: dict[str, Decimal] = {}
        for open_order in self._orders.values():
            quantity = open_order.order.quantity
            if open_order.order.side is OrderSide.SELL:
                quantity = -quantity
            instrument_id = open_order.order.instrument_id
            quantities[instrument_id] = quantities.get(instrument_id, Decimal(0)) + quantity
        return quantities
