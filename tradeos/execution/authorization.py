"""Deterministic execution authorization boundary."""

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum

from .models import Order


class OperatingMode(StrEnum):
    """TradeOS operating modes relevant to execution authority."""

    RESEARCH = "RESEARCH"
    PAPER = "PAPER"
    ASSISTED_LIVE = "ASSISTED_LIVE"
    CONTROLLED_AUTONOMOUS = "CONTROLLED_AUTONOMOUS"
    EMERGENCY = "EMERGENCY"


class AuthorizationStatus(StrEnum):
    """Lifecycle state tracked by the authorization ledger."""

    ACTIVE = "ACTIVE"
    CONSUMED = "CONSUMED"
    REVOKED = "REVOKED"


@dataclass(frozen=True, slots=True)
class ExecutionAuthorization:
    """Immutable, order-specific permission to cross the execution boundary."""

    authorization_id: str
    proposal_id: str
    risk_decision_id: str
    account_id: str
    instrument_id: str
    approved_quantity: Decimal
    min_price: Decimal | None
    max_price: Decimal | None
    approved_stop_price: Decimal | None
    operating_mode: OperatingMode
    configuration_hash: str
    issued_at: datetime
    expires_at: datetime

    def validate(self) -> None:
        """Validate authorization identity, scope, and expiry invariants."""
        required_ids = (
            self.authorization_id,
            self.proposal_id,
            self.risk_decision_id,
            self.account_id,
            self.instrument_id,
            self.configuration_hash,
        )
        if any(not value for value in required_ids):
            raise ValueError("authorization identifiers must not be empty")
        if self.approved_quantity <= 0:
            raise ValueError("approved_quantity must be greater than zero")
        if self.min_price is not None and self.min_price <= 0:
            raise ValueError("min_price must be positive")
        if self.max_price is not None and self.max_price <= 0:
            raise ValueError("max_price must be positive")
        if self.min_price is not None and self.max_price is not None and self.min_price > self.max_price:
            raise ValueError("min_price cannot exceed max_price")
        if self.approved_stop_price is not None and self.approved_stop_price <= 0:
            raise ValueError("approved_stop_price must be positive")
        if self.issued_at.tzinfo is None or self.issued_at.utcoffset() is None:
            raise ValueError("issued_at must be timezone-aware")
        if self.expires_at.tzinfo is None or self.expires_at.utcoffset() is None:
            raise ValueError("expires_at must be timezone-aware")
        if self.issued_at.tzinfo is not UTC or self.expires_at.tzinfo is not UTC:
            raise ValueError("authorization timestamps must use UTC")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must be after issued_at")
        if self.operating_mode in {OperatingMode.RESEARCH, OperatingMode.EMERGENCY}:
            raise ValueError("operating mode does not permit execution")

    def permits(self, order: Order, now: datetime) -> bool:
        """Return whether this authorization permits the exact order at ``now``."""
        self.validate()
        order.validate()
        if now.tzinfo is None or now.utcoffset() is None or now.tzinfo is not UTC:
            raise ValueError("now must use UTC")
        if now < self.issued_at or now >= self.expires_at:
            return False
        if order.instrument_id != self.instrument_id:
            return False
        if order.quantity != self.approved_quantity:
            return False
        if self.min_price is not None or self.max_price is not None:
            return False
        return True


class AuthorizationLedger:
    """Deterministically prevent reuse of an execution authorization."""

    def __init__(self) -> None:
        self._authorizations: dict[str, ExecutionAuthorization] = {}
        self._consumed: set[str] = set()

    def issue(self, authorization: ExecutionAuthorization) -> None:
        """Register a new authorization, rejecting duplicate identifiers."""
        authorization.validate()
        if authorization.authorization_id in self._authorizations:
            raise ValueError("authorization_id already exists")
        self._authorizations[authorization.authorization_id] = authorization

    def revoke(self, authorization_id: str) -> None:
        """Revoke an active authorization."""
        if authorization_id not in self._authorizations:
            raise KeyError(f"unknown authorization: {authorization_id}")
        if authorization_id in self._consumed:
            raise ValueError("consumed authorization cannot be revoked")
        del self._authorizations[authorization_id]

    def consume(self, authorization_id: str) -> ExecutionAuthorization:
        """Consume an authorization exactly once and return its immutable record."""
        authorization = self._authorizations.get(authorization_id)
        if authorization is None:
            raise KeyError(f"unknown authorization: {authorization_id}")
        if authorization_id in self._consumed:
            raise ValueError("authorization already consumed")
        self._consumed.add(authorization_id)
        return authorization

    def status(self, authorization_id: str) -> AuthorizationStatus:
        """Return the current ledger status for an authorization."""
        if authorization_id not in self._authorizations:
            raise KeyError(f"unknown authorization: {authorization_id}")
        if authorization_id in self._consumed:
            return AuthorizationStatus.CONSUMED
        return AuthorizationStatus.ACTIVE


class ExecutionAuthorizationPolicy:
    """Evaluate deterministic prerequisites for issuing execution authority."""

    @staticmethod
    def issue(
        authorization: ExecutionAuthorization,
        *,
        risk_approved: bool,
        human_approved: bool = False,
    ) -> ExecutionAuthorization:
        """Return authorization only when risk and operating-mode policy permit it."""
        authorization.validate()
        if not risk_approved:
            raise PermissionError("risk approval is required")
        if authorization.operating_mode is OperatingMode.ASSISTED_LIVE and not human_approved:
            raise PermissionError("human approval is required for ASSISTED_LIVE")
        return authorization
