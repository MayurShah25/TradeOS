from decimal import Decimal

import pytest

from tradeos.portfolio.account_state import AccountState, AccountStateBuilder


def test_account_state_preserves_explicit_values() -> None:
    account = AccountStateBuilder.snapshot(
        cash=Decimal("10000"),
        buying_power=Decimal("15000"),
        equity=Decimal("12000"),
        margin_used=Decimal("2000"),
        available_margin=Decimal("8000"),
    )

    assert account == AccountState(
        cash=Decimal("10000"),
        buying_power=Decimal("15000"),
        equity=Decimal("12000"),
        margin_used=Decimal("2000"),
        available_margin=Decimal("8000"),
    )


def test_account_state_is_immutable() -> None:
    account = AccountStateBuilder.snapshot(
        cash=Decimal("10000"),
        buying_power=Decimal("10000"),
        equity=Decimal("10000"),
    )

    with pytest.raises(AttributeError):
        account.cash = Decimal("1")


def test_negative_margin_is_rejected() -> None:
    with pytest.raises(ValueError, match="margin_used"):
        AccountStateBuilder.snapshot(
            cash=Decimal("10000"),
            buying_power=Decimal("10000"),
            equity=Decimal("10000"),
            margin_used=Decimal("-1"),
        )


def test_negative_available_margin_is_rejected() -> None:
    with pytest.raises(ValueError, match="available_margin"):
        AccountStateBuilder.snapshot(
            cash=Decimal("10000"),
            buying_power=Decimal("10000"),
            equity=Decimal("10000"),
            available_margin=Decimal("-1"),
        )
