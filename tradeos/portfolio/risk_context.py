"""Deterministic risk context assembled from a coherent portfolio snapshot."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from .exposure import ExposureCalculator, ExposureSnapshot
from .heat import PortfolioHeat
from .open_orders import OpenOrderLedger
from .portfolio_state import PortfolioState
from .position_ledger import PositionLedger


@dataclass(frozen=True, slots=True)
class RiskContext:
    """Immutable portfolio context consumed by deterministic risk controls."""

    portfolio: PortfolioState
    exposure: ExposureSnapshot
    heat: PortfolioHeat
    as_of: datetime
    stale: bool

    def validate(self) -> None:
        """Validate context consistency and UTC freshness metadata."""
        self.portfolio.validate()
        if self.as_of.tzinfo is None or self.as_of.utcoffset() is None:
            raise ValueError("as_of must be timezone-aware")
        if self.as_of.tzinfo is not UTC:
            raise ValueError("as_of must use UTC")
        self.exposure.validate()
        if self.heat.gross_exposure != self.exposure.gross:
            raise ValueError("heat and exposure gross values must match")


class RiskContextBuilder:
    """Build deterministic risk context from one portfolio snapshot."""

    @staticmethod
    def build(
        portfolio: PortfolioState,
        prices: dict[str, Decimal],
        as_of: datetime,
        max_age: timedelta,
    ) -> RiskContext:
        """Return a validated context with exposure, heat, and stale-state flag."""
        if max_age < timedelta(0):
            raise ValueError("max_age cannot be negative")
        if as_of.tzinfo is None or as_of.utcoffset() is None:
            raise ValueError("as_of must be timezone-aware")
        if as_of.tzinfo is not UTC:
            raise ValueError("as_of must use UTC")
        if as_of < portfolio.timestamp:
            raise ValueError("as_of cannot precede portfolio timestamp")
        if portfolio.account is None:
            raise ValueError("account state is required for risk context")

        position_ledger = PositionLedger.from_positions(portfolio.positions)
        open_order_ledger = OpenOrderLedger()
        for open_order in portfolio.open_orders:
            open_order_ledger.add(open_order)

        exposure = ExposureCalculator.from_positions(
            position_ledger, prices, open_order_ledger
        )
        heat = PortfolioHeat.calculate(exposure.gross, portfolio.account.equity)
        stale = as_of - portfolio.timestamp > max_age
        context = RiskContext(portfolio, exposure, heat, as_of, stale)
        context.validate()
        return context
