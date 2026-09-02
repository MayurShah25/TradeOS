"""Deterministic account state primitives."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class AccountState:
    """Immutable snapshot of externally reported account values."""

    cash: Decimal
    buying_power: Decimal
    equity: Decimal
    margin_used: Decimal = Decimal(0)
    available_margin: Decimal = Decimal(0)

    def validate(self) -> None:
        """Validate deterministic account-state invariants."""
        values = {
            "cash": self.cash,
            "buying_power": self.buying_power,
            "equity": self.equity,
            "margin_used": self.margin_used,
            "available_margin": self.available_margin,
        }
        for name, value in values.items():
            if not isinstance(value, Decimal):
                raise TypeError(f"{name} must be a Decimal")
        if self.margin_used < Decimal(0):
            raise ValueError("margin_used cannot be negative")
        if self.available_margin < Decimal(0):
            raise ValueError("available_margin cannot be negative")


@dataclass(frozen=True, slots=True)
class AccountStateBuilder:
    """Build validated account snapshots from explicit external state."""

    @staticmethod
    def snapshot(
        cash: Decimal,
        buying_power: Decimal,
        equity: Decimal,
        margin_used: Decimal = Decimal(0),
        available_margin: Decimal = Decimal(0),
    ) -> AccountState:
        """Create and validate an immutable account-state snapshot."""
        account = AccountState(
            cash=cash,
            buying_power=buying_power,
            equity=equity,
            margin_used=margin_used,
            available_margin=available_margin,
        )
        account.validate()
        return account
