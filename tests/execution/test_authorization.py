"""Tests for the deterministic execution authorization boundary."""

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from tradeos.execution import (
    AuthorizationLedger,
    AuthorizationStatus,
    ExecutionAuthorization,
    ExecutionAuthorizationPolicy,
    OperatingMode,
    Order,
    OrderSide,
)


NOW = datetime(2026, 9, 2, 9, 0, tzinfo=UTC)


def _authorization(mode: OperatingMode = OperatingMode.PAPER) -> ExecutionAuthorization:
    return ExecutionAuthorization(
        authorization_id="auth-1",
        proposal_id="proposal-1",
        risk_decision_id="risk-1",
        account_id="account-1",
        instrument_id="AAPL",
        approved_quantity=Decimal(10),
        min_price=None,
        max_price=None,
        approved_stop_price=None,
        operating_mode=mode,
        configuration_hash="config-hash",
        issued_at=NOW,
        expires_at=NOW + timedelta(minutes=5),
    )


def _order(quantity: Decimal = Decimal(10), instrument: str = "AAPL") -> Order:
    return Order("order-1", instrument, OrderSide.BUY, quantity)


def test_authorization_policy_requires_risk_approval() -> None:
    with pytest.raises(PermissionError, match="risk approval"):
        ExecutionAuthorizationPolicy.issue(_authorization(), risk_approved=False)


def test_assisted_live_requires_human_approval() -> None:
    with pytest.raises(PermissionError, match="human approval"):
        ExecutionAuthorizationPolicy.issue(
            _authorization(OperatingMode.ASSISTED_LIVE),
            risk_approved=True,
        )


def test_policy_accepts_paper_authorization_after_risk_approval() -> None:
    authorization = ExecutionAuthorizationPolicy.issue(
        _authorization(), risk_approved=True
    )

    assert authorization.authorization_id == "auth-1"


def test_research_and_emergency_modes_cannot_issue_authorization() -> None:
    for mode in (OperatingMode.RESEARCH, OperatingMode.EMERGENCY):
        with pytest.raises(ValueError, match="does not permit execution"):
            _authorization(mode).validate()


def test_authorization_is_specific_to_order_and_expiry() -> None:
    authorization = _authorization()

    assert authorization.permits(_order(), NOW + timedelta(minutes=1)) is True
    assert authorization.permits(_order(Decimal(11)), NOW + timedelta(minutes=1)) is False
    assert authorization.permits(_order(instrument="MSFT"), NOW + timedelta(minutes=1)) is False
    assert authorization.permits(_order(), NOW + timedelta(minutes=5)) is False


def test_authorization_ledger_prevents_reuse() -> None:
    ledger = AuthorizationLedger()
    authorization = _authorization()
    ledger.issue(authorization)

    assert ledger.status("auth-1") is AuthorizationStatus.ACTIVE
    consumed = ledger.consume("auth-1")
    assert consumed == authorization
    assert ledger.status("auth-1") is AuthorizationStatus.CONSUMED

    with pytest.raises(ValueError, match="already consumed"):
        ledger.consume("auth-1")


def test_authorization_ledger_rejects_duplicate_and_consumed_revoke() -> None:
    ledger = AuthorizationLedger()
    authorization = _authorization()
    ledger.issue(authorization)

    with pytest.raises(ValueError, match="already exists"):
        ledger.issue(authorization)

    ledger.consume("auth-1")
    with pytest.raises(ValueError, match="cannot be revoked"):
        ledger.revoke("auth-1")


def test_authorization_rejects_invalid_expiry() -> None:
    authorization = replace(_authorization(), expires_at=NOW)

    with pytest.raises(ValueError, match="expires_at"):
        authorization.validate()
