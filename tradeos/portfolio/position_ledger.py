"""Deterministic position accounting from executed fills."""

from dataclasses import dataclass
from decimal import Decimal

from tradeos.execution import OrderSide


@dataclass(frozen=True, slots=True)
class Position:
    """Immutable position snapshot for one instrument."""

    instrument_id: str
    quantity: Decimal
    average_price: Decimal
    realized_pnl: Decimal


class PositionLedger:
    """Apply executed fills to deterministic position state."""

    def __init__(self) -> None:
        self._positions: dict[str, Position] = {}

    def get(self, instrument_id: str) -> Position | None:
        """Return the current position for an instrument."""
        return self._positions.get(instrument_id)

    def apply_fill(
        self,
        instrument_id: str,
        side: OrderSide,
        quantity: Decimal,
        price: Decimal,
    ) -> Position:
        """Apply one executed fill and return the resulting position."""
        if not instrument_id:
            raise ValueError("instrument_id must not be empty")
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        if price <= 0:
            raise ValueError("price must be positive")

        current = self._positions.get(
            instrument_id,
            Position(instrument_id, Decimal(0), Decimal(0), Decimal(0)),
        )
        signed_fill = quantity if side is OrderSide.BUY else -quantity
        old_qty = current.quantity
        new_qty = old_qty + signed_fill

        if old_qty == 0 or old_qty * signed_fill > 0:
            total_cost = abs(old_qty) * current.average_price + quantity * price
            average_price = total_cost / abs(new_qty)
            realized_pnl = current.realized_pnl
        else:
            closed_quantity = min(abs(old_qty), quantity)
            direction = Decimal(1) if old_qty > 0 else Decimal(-1)
            realized_pnl = current.realized_pnl + (
                (price - current.average_price) * closed_quantity * direction
            )
            if new_qty == 0:
                average_price = Decimal(0)
            elif old_qty * new_qty > 0:
                average_price = current.average_price
            else:
                average_price = price

        position = Position(instrument_id, new_qty, average_price, realized_pnl)
        self._positions[instrument_id] = position
        return position
