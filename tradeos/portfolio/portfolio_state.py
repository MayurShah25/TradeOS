"""Immutable portfolio snapshots from explicit portfolio state inputs."""

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

from .account_state import AccountState
from .open_orders import OpenOrder
from .position_ledger import Position, PositionLedger


@dataclass(frozen=True, slots=True)
class PortfolioState:
    """Immutable snapshot of account, positions, open orders, and P&L."""

    account: AccountState
    positions: tuple[Position, ...]
    open_orders: tuple[OpenOrder, ...]
    realized_pnl: Decimal
    timestamp: datetime

    def position_for(self, instrument_id: str) -> Position | None:
        """Return the position for an instrument, if present."""
        return next(
            (position for position in self.positions if position.instrument_id == instrument_id),
            None,
        )

    def validate(self) -> None:
        """Validate portfolio snapshot freshness metadata."""
        self.account.validate()
        if self.timestamp.tzinfo is None or self.timestamp.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware")
        if self.timestamp.tzinfo != timezone.utc:
            raise ValueError("timestamp must use UTC")


class PortfolioStateBuilder:
    """Build immutable portfolio snapshots from deterministic state inputs."""

    @staticmethod
    def snapshot(
        ledger: PositionLedger,
        account: AccountState,
        open_orders: tuple[OpenOrder, ...] = (),
        timestamp: datetime | None = None,
    ) -> PortfolioState:
        """Return a validated immutable portfolio snapshot."""
        positions = tuple(ledger.positions())
        realized_pnl = sum((position.realized_pnl for position in positions), Decimal(0))
        snapshot_time = timestamp if timestamp is not None else datetime.now(timezone.utc)
        state = PortfolioState(
            account=account,
            positions=positions,
            open_orders=tuple(open_orders),
            realized_pnl=realized_pnl,
            timestamp=snapshot_time,
        )
        state.validate()
        return state
