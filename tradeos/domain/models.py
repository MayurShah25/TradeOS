"""Core TradeOS domain models.

These models represent lifecycle facts and requests. They intentionally do not
perform authorization, risk approval, broker submission, or state transitions.
Those responsibilities belong to deterministic application services.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum


class TradeProposalStatus(StrEnum):
    PROPOSED = "PROPOSED"
    REJECTED = "REJECTED"
    ACCEPTED = "ACCEPTED"


class RiskDecisionStatus(StrEnum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    REVIEW = "REVIEW"


@dataclass(frozen=True, slots=True)
class TradeProposal:
    proposal_id: str
    instrument_id: str
    side: str
    quantity: Decimal
    created_at: datetime
    strategy_id: str
    strategy_version: str
    status: TradeProposalStatus = TradeProposalStatus.PROPOSED


@dataclass(frozen=True, slots=True)
class RiskDecision:
    decision_id: str
    proposal_id: str
    status: RiskDecisionStatus
    decided_at: datetime
    reason: str


@dataclass(frozen=True, slots=True)
class ExecutionAuthorization:
    authorization_id: str
    proposal_id: str
    decision_id: str
    issued_at: datetime
    expires_at: datetime
    consumed: bool = False


@dataclass(frozen=True, slots=True)
class OrderIntent:
    intent_id: str
    authorization_id: str
    instrument_id: str
    side: str
    quantity: Decimal
    created_at: datetime


@dataclass(frozen=True, slots=True)
class Order:
    order_id: str
    intent_id: str
    submitted_at: datetime
    broker_order_id: str | None = None


@dataclass(frozen=True, slots=True)
class Fill:
    fill_id: str
    order_id: str
    quantity: Decimal
    price: Decimal
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class Position:
    position_id: str
    instrument_id: str
    quantity: Decimal
    average_price: Decimal
    as_of: datetime


@dataclass(frozen=True, slots=True)
class Trade:
    trade_id: str
    proposal_id: str
    instrument_id: str
    opened_at: datetime
    closed_at: datetime | None = None
