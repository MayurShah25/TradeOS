from decimal import Decimal

from tradeos.execution import Order, OrderSide
from tradeos.portfolio.open_orders import OpenOrderLedger
from tradeos.portfolio.position_ledger import PositionLedger
from tradeos.portfolio.pre_trade_impact import PreTradeImpactCalculator
from tradeos.portfolio.risk_gate import RiskDecision, RiskGate, RiskLimits


def make_impact() -> object:
    return PreTradeImpactCalculator.calculate(
        PositionLedger(),
        OpenOrderLedger(),
        {"AAPL": Decimal(100)},
        Decimal(10000),
        Order("o1", "AAPL", OrderSide.BUY, Decimal(10)),
    )


def test_risk_gate_approves_within_limits() -> None:
    result = RiskGate.evaluate(make_impact(), RiskLimits(Decimal(2000), Decimal("0.2")))
    assert result.decision is RiskDecision.APPROVE
    assert result.reasons == ()


def test_risk_gate_rejects_excess_gross_exposure() -> None:
    result = RiskGate.evaluate(make_impact(), RiskLimits(Decimal(500), Decimal("0.2")))
    assert result.decision is RiskDecision.REJECT
    assert "max_gross_exposure exceeded" in result.reasons


def test_risk_gate_rejects_excess_heat() -> None:
    result = RiskGate.evaluate(make_impact(), RiskLimits(Decimal(2000), Decimal("0.05")))
    assert result.decision is RiskDecision.REJECT
    assert "max_portfolio_heat exceeded" in result.reasons
