from datetime import UTC, datetime
from decimal import Decimal

from tradeos.domain import (
    ExecutionAuthorization,
    Fill,
    Order,
    OrderIntent,
    Position,
    RiskDecision,
    Trade,
    TradeProposal,
)
from tradeos.domain.models import RiskDecisionStatus, TradeProposalStatus


def test_domain_models_and_defaults() -> None:
    now = datetime.now(UTC)

    proposal = TradeProposal(
        proposal_id="proposal-1",
        instrument_id="AAPL",
        side="BUY",
        quantity=Decimal("10"),
        created_at=now,
        strategy_id="strategy-1",
        strategy_version="1.0",
    )
    decision = RiskDecision(
        decision_id="decision-1",
        proposal_id=proposal.proposal_id,
        status=RiskDecisionStatus.APPROVED,
        decided_at=now,
        reason="within limits",
    )
    authorization = ExecutionAuthorization(
        authorization_id="auth-1",
        proposal_id=proposal.proposal_id,
        decision_id=decision.decision_id,
        issued_at=now,
        expires_at=now,
    )
    intent = OrderIntent(
        intent_id="intent-1",
        authorization_id=authorization.authorization_id,
        instrument_id=proposal.instrument_id,
        side=proposal.side,
        quantity=proposal.quantity,
        created_at=now,
    )
    order = Order(
        order_id="order-1",
        intent_id=intent.intent_id,
        submitted_at=now,
    )
    fill = Fill(
        fill_id="fill-1",
        order_id=order.order_id,
        quantity=Decimal("10"),
        price=Decimal("200.00"),
        occurred_at=now,
    )
    position = Position(
        position_id="position-1",
        instrument_id=proposal.instrument_id,
        quantity=fill.quantity,
        average_price=fill.price,
        as_of=now,
    )
    trade = Trade(
        trade_id="trade-1",
        proposal_id=proposal.proposal_id,
        instrument_id=proposal.instrument_id,
        opened_at=now,
    )

    assert proposal.status is TradeProposalStatus.PROPOSED
    assert proposal.quantity == Decimal("10")
    assert decision.status is RiskDecisionStatus.APPROVED
    assert authorization.consumed is False
    assert intent.authorization_id == authorization.authorization_id
    assert order.broker_order_id is None
    assert fill.price == Decimal("200.00")
    assert position.average_price == fill.price
    assert trade.closed_at is None
