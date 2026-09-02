"""Deterministic gross and net portfolio exposure calculations."""

from dataclasses import dataclass
from decimal import Decimal

from tradeos.portfolio.open_orders import OpenOrderLedger
from tradeos.portfolio.position_ledger import PositionLedger


@dataclass(frozen=True, slots=True)
class ExposureSnapshot:
    """Immutable gross and net exposure snapshot."""

    gross: Decimal
    net: Decimal

    def validate(self) -> None:
        """Validate exposure values."""
        if self.gross < 0:
            raise ValueError("gross exposure cannot be negative")
        if abs(self.net) > self.gross:
            raise ValueError("absolute net exposure cannot exceed gross exposure")


class ExposureCalculator:
    """Calculate exposure from positions and accepted open orders."""

    @staticmethod
    def from_positions(
        positions: PositionLedger,
        prices: dict[str, Decimal],
        open_orders: OpenOrderLedger | None = None,
    ) -> ExposureSnapshot:
        """Calculate marked gross and net exposure using explicit prices."""
        gross = Decimal(0)
        net = Decimal(0)
        for position in positions.positions():
            price = prices.get(position.instrument_id)
            if price is None:
                raise ValueError(f"missing price for {position.instrument_id}")
            if price <= 0:
                raise ValueError("price must be positive")
            value = position.quantity * price
            gross += abs(value)
            net += value

        if open_orders is not None:
            for open_order in open_orders.orders():
                price = prices.get(open_order.order.instrument_id)
                if price is None:
                    raise ValueError(f"missing price for {open_order.order.instrument_id}")
                if price <= 0:
                    raise ValueError("price must be positive")
                value = open_order.order.quantity * price
                if open_order.order.side.value == "SELL":
                    value = -value
                gross += abs(value)
                net += value

        snapshot = ExposureSnapshot(gross, net)
        snapshot.validate()
        return snapshot
