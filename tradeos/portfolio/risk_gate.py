"""Deterministic portfolio risk gate."""

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from tradeos.portfolio.pre_trade_impact import PreTradeImpact


class RiskDecision(StrEnum):
    """Authoritative deterministic risk outcome."""

    APPROVE = "APPROVE"
    REJECT = "REJECT"


@dataclass(frozen=True, slots=True)
class RiskLimits:
    """Hard portfolio limits used by the risk gate."""

    max_gross_exposure: Decimal
    max_portfolio_heat: Decimal

    def validate(self) -> None:
        """Validate configured hard limits."""
        if self.max_gross_exposure < 0:
            raise ValueError("max_gross_exposure cannot be negative")
        if self.max_portfolio_heat < 0:
            raise ValueError("max_portfolio_heat cannot be negative")


@dataclass(frozen=True, slots=True)
class RiskResult:
    """Immutable risk-gate decision and deterministic reasons."""

    decision: RiskDecision
    reasons: tuple[str, ...]


class RiskGate:
    """Evaluate projected portfolio state against hard risk limits."""

    @staticmethod
    def evaluate(impact: PreTradeImpact, limits: RiskLimits) -> RiskResult:
        """Approve only when all projected hard limits remain within bounds."""
        limits.validate()
        reasons: list[str] = []
        if impact.projected_exposure.gross > limits.max_gross_exposure:
            reasons.append("max_gross_exposure exceeded")
        if impact.projected_heat.ratio > limits.max_portfolio_heat:
            reasons.append("max_portfolio_heat exceeded")
        if reasons:
            return RiskResult(RiskDecision.REJECT, tuple(reasons))
        return RiskResult(RiskDecision.APPROVE, ())
