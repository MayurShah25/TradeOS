"""Immutable portfolio state derived from reconciled execution fills."""

from dataclasses import dataclass
from decimal import Decimal

from .position_ledger import Position, PositionLedger


@dataclass(frozen=True, slots=True)
class PortfolioState:
    """Immutable snapshot of portfolio positions and realized P&L."""

    positions: tuple[Position, ...]
    realized_pnl: Decimal

    def position_for(self, instrument_id: str) -> Position | None:
        """Return the position for an instrument, if present."""
        return next(
            (
                position
                for position in self.positions
                if position.instrument_id == instrument_id
            ),
            None,
        )


class PortfolioStateBuilder:
    """Build portfolio snapshots from a deterministic position ledger."""

    @staticmethod
    def snapshot(ledger: PositionLedger) -> PortfolioState:
        """Return an immutable snapshot of all current positions."""
        positions = tuple(ledger.positions())
        realized_pnl = sum((position.realized_pnl for position in positions), Decimal(0))
        return PortfolioState(positions=positions, realized_pnl=realized_pnl)
