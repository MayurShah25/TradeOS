"""Immutable portfolio snapshots from explicit portfolio state inputs."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal

from .account_state import AccountState
from .open_orders import OpenOrder
from .position_ledger import Position, PositionLedger


@dataclass(frozen=True, slots=True)
class PortfolioState:
    """Immutable snapshot of positions, account state, and pending orders."""

    positions: tuple[Position, ...]
    realized_pnl: Decimal
    account: AccountState | None = None
    open_orders: tuple[OpenOrder, ...] = ()
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def position_for(self, instrument_id: str) -> Position | None:
        """Return the position for an instrument, if present."""
        return next(
            (position for position in self.positions if position.instrument_id == instrument_id),
            None,
        )

    def validate(self) -> None:
        """Validate portfolio snapshot invariants and freshness metadata."""
        if self.account is not None:
            self.account.validate()
        if self.timestamp.tzinfo is None or self.timestamp.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware")
        if self.timestamp.tzinfo is not UTC:
            raise ValueError("timestamp must use UTC")


class PortfolioStateBuilder:
    """Build immutable portfolio snapshots from deterministic state inputs."""

    @staticmethod
    def snapshot(
        ledger: PositionLedger,
        account: AccountState | None = None,
        open_orders: tuple[OpenOrder, ...] = (),
        timestamp: datetime | None = None,
    ) -> PortfolioState:
        """Return a validated immutable portfolio snapshot."""
        positions = tuple(ledger.positions())
        realized_pnl = sum((position.realized_pnl for position in positions), Decimal(0))
        snapshot_time = timestamp if timestamp is not None else datetime.now(UTC)
        state = PortfolioState(
            positions=positions,
            realized_pnl=realized_pnl,
            account=account,
            open_orders=tuple(open_orders),
            timestamp=snapshot_time,
        )
        state.validate()
        return state
