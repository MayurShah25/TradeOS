"""Deterministic expanded portfolio risk controls."""

from dataclasses import dataclass
from decimal import Decimal

from tradeos.execution import Order

from .open_orders import OpenOrderLedger
from .position_ledger import PositionLedger
from .pre_trade_impact import PreTradeImpactCalculator
from .risk_context import RiskContext


@dataclass(frozen=True, slots=True)
class PortfolioRiskLimits:
    """Hard limits for portfolio-level risk controls."""

    max_gross_exposure: Decimal
    max_portfolio_heat: Decimal
    max_leverage: Decimal
    min_available_margin: Decimal

    def validate(self) -> None:
        """Validate configured portfolio risk limits."""
        if self.max_gross_exposure < 0:
            raise ValueError("max_gross_exposure cannot be negative")
        if self.max_portfolio_heat < 0:
            raise ValueError("max_portfolio_heat cannot be negative")
        if self.max_leverage < 0:
            raise ValueError("max_leverage cannot be negative")
        if self.min_available_margin < 0:
            raise ValueError("min_available_margin cannot be negative")


@dataclass(frozen=True, slots=True)
class PortfolioRiskResult:
    """Immutable deterministic portfolio risk evaluation."""

    approved: bool
    reasons: tuple[str, ...]


class PortfolioRiskControls:
    """Evaluate a coherent risk context against hard portfolio limits."""

    @staticmethod
    def evaluate(
        context: RiskContext,
        limits: PortfolioRiskLimits,
        order: Order | None = None,
        prices: dict[str, Decimal] | None = None,
    ) -> PortfolioRiskResult:
        """Approve only when freshness and all applicable hard limits pass."""
        limits.validate()
        context.validate()
        reasons: list[str] = []

        if context.stale:
            reasons.append("portfolio risk context is stale")

        exposure = context.exposure
        heat = context.heat
        if order is not None:
            if prices is None:
                reasons.append("prices are required for pre-trade impact")
            else:
                account = context.portfolio.account
                if account is None:
                    reasons.append("account state is required")
                else:
                    impact = PreTradeImpactCalculator.calculate(
                        PositionLedger.from_positions(context.portfolio.positions),
                        OpenOrderLedger.from_orders(context.portfolio.open_orders),
                        prices,
                        account.equity,
                        order,
                    )
                    exposure = impact.projected_exposure
                    heat = impact.projected_heat

        if exposure.gross > limits.max_gross_exposure:
            reasons.append("max_gross_exposure exceeded")
        if heat.ratio > limits.max_portfolio_heat:
            reasons.append("max_portfolio_heat exceeded")

        account = context.portfolio.account
        if account is None:
            reasons.append("account state is required")
        else:
            if account.equity <= 0:
                reasons.append("equity must be positive")
            else:
                leverage = exposure.gross / account.equity
                if leverage > limits.max_leverage:
                    reasons.append("max_leverage exceeded")
            if account.available_margin < limits.min_available_margin:
                reasons.append("minimum available margin violated")

        if reasons:
            return PortfolioRiskResult(False, tuple(reasons))
        return PortfolioRiskResult(True, ())
