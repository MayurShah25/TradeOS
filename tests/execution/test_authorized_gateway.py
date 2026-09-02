"""Tests for the deterministic authorized execution gateway."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from tradeos.execution import (
    AuthorizationLedger,
    AuthorizedExecutionGateway,
    ExecutionAuthorization,
    OperatingMode,
    Order,
    OrderSide,
    PaperBroker,
)

NOW = datetime(2026, 9, 2, 10, 0, tzinfo=UTC)


def _order(quantity: str = "2") -> Order:
    return Order("order-1", "AAPL", OrderSide.BUY, Decimal(quantity))


def _authorization(quantity: str = "2") -> ExecutionAuthorization:
    return ExecutionAuthorization(
        authorization_id="auth-1",
        proposal_id="proposal-1",
        risk_decision_id="risk-1",
        account_id="account-1",
        instrument_id="AAPL",
        approved_quantity=Decimal(quantity),
        min_price=None,
        max_price=None,
        approved_stop_price=None,
        operating_mode=OperatingMode.PAPER,
        configuration_hash="config-hash",
        issued_at=NOW - timedelta(minutes=1),
        expires_at=NOW + timedelta(minutes=5),
    )


def _gateway() -> tuple[AuthorizedExecutionGateway, AuthorizationLedger]:
    ledger = AuthorizationLedger()
    ledger.issue(_authorization())
    return AuthorizedExecutionGateway(PaperBroker(), ledger), ledger


def test_gateway_executes_authorized_order() -> None:
    gateway, ledger = _gateway()

    result = gateway.execute("auth-1", _order(), NOW)

    assert result.authorization_id == "auth-1"
    assert result.order_id == "order-1"
    assert result.status.value == "FILLED"
    assert ledger.status("auth-1").value == "CONSUMED"


def test_gateway_rejects_wrong_order_without_consuming_authorization() -> None:
    gateway, ledger = _gateway()

    with pytest.raises(PermissionError, match="does not permit"):
        gateway.execute("auth-1", _order("3"), NOW)

    assert ledger.status("auth-1").value == "ACTIVE"


def test_gateway_rejects_expired_authorization_without_consuming_it() -> None:
    gateway, ledger = _gateway()

    with pytest.raises(PermissionError, match="does not permit"):
        gateway.execute("auth-1", _order(), NOW + timedelta(minutes=6))

    assert ledger.status("auth-1").value == "ACTIVE"


def test_gateway_prevents_authorization_reuse() -> None:
    gateway, ledger = _gateway()

    gateway.execute("auth-1", _order(), NOW)

    with pytest.raises(ValueError, match="already consumed"):
        gateway.execute("auth-1", _order(), NOW)

    assert ledger.status("auth-1").value == "CONSUMED"


def test_gateway_rejects_unknown_authorization() -> None:
    ledger = AuthorizationLedger()
    gateway = AuthorizedExecutionGateway(PaperBroker(), ledger)

    with pytest.raises(KeyError, match="unknown authorization"):
        gateway.execute("missing", _order(), NOW)
