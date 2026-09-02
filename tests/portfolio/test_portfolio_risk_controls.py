"""Tests for deterministic expanded portfolio risk controls."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from tradeos.execution import Order, OrderSide
from tradeos.portfolio import (
    AccountStateBuilder,
    PortfolioRiskControls,
    PortfolioRiskLimits,
    PortfolioStateBuilder,
    PositionLedger,
    RiskContextBuilder,
)


def _context(
    *,
    as_of_offset: timedelta = timedelta(0),
    equity: Decimal = Decimal(10000),
    available_margin: Decimal = Decimal(5000),
):
    timestamp = datetime(2026, 9, 2, 8, 0, tzinfo=UTC)
    ledger = PositionLedger()
    ledger.apply_fill("AAPL", OrderSide.BUY, Decimal(10), Decimal(100))
    account = AccountStateBuilder.snapshot(
        cash=Decimal(9000),
        buying_power=Decimal(18000),
        equity=equity,
        available_margin=available_margin,
    )
    portfolio = PortfolioStateBuilder.snapshot(ledger, account, (), timestamp)
    as_of = timestamp + as_of_offset
    return RiskContextBuilder.build(portfolio, {"AAPL": Decimal(120)}, as_of, timedelta(minutes=5))


def _limits() -> PortfolioRiskLimits:
    return PortfolioRiskLimits(
        max_gross_exposure=Decimal(5000),
        max_portfolio_heat=Decimal("0.5"),
        max_leverage=Decimal(1),
        min_available_margin=Decimal(1000),
    )


def test_portfolio_risk_controls_approve_valid_context() -> None:
    result = PortfolioRiskControls.evaluate(_context(), _limits())

    assert result.approved is True
    assert result.reasons == ()


def test_stale_context_is_authoritatively_rejected() -> None:
    result = PortfolioRiskControls.evaluate(_context(as_of_offset=timedelta(minutes=6)), _limits())

    assert result.approved is False
    assert "portfolio risk context is stale" in result.reasons


def test_leverage_limit_is_enforced() -> None:
    limits = PortfolioRiskLimits(
        max_gross_exposure=Decimal(5000),
        max_portfolio_heat=Decimal("0.5"),
        max_leverage=Decimal("0.1"),
        min_available_margin=Decimal(1000),
    )

    result = PortfolioRiskControls.evaluate(_context(), limits)

    assert result.approved is False
    assert "max_leverage exceeded" in result.reasons


def test_minimum_available_margin_is_enforced() -> None:
    limits = PortfolioRiskLimits(
        max_gross_exposure=Decimal(5000),
        max_portfolio_heat=Decimal("0.5"),
        max_leverage=Decimal(1),
        min_available_margin=Decimal(6000),
    )

    result = PortfolioRiskControls.evaluate(_context(), limits)

    assert result.approved is False
    assert "minimum available margin violated" in result.reasons


def test_pre_trade_order_is_evaluated_against_projected_exposure() -> None:
    order = Order("order-1", "AAPL", OrderSide.BUY, Decimal(30))
    limits = PortfolioRiskLimits(
        max_gross_exposure=Decimal(4000),
        max_portfolio_heat=Decimal("0.5"),
        max_leverage=Decimal(1),
        min_available_margin=Decimal(1000),
    )

    result = PortfolioRiskControls.evaluate(
        _context(),
        limits,
        order=order,
        prices={"AAPL": Decimal(120)},
    )

    assert result.approved is False
    assert "max_gross_exposure exceeded" in result.reasons


def test_pre_trade_order_requires_prices() -> None:
    order = Order("order-1", "AAPL", OrderSide.BUY, Decimal(1))

    result = PortfolioRiskControls.evaluate(_context(), _limits(), order=order)

    assert result.approved is False
    assert "prices are required for pre-trade impact" in result.reasons


def test_limits_reject_negative_values() -> None:
    limits = PortfolioRiskLimits(
        max_gross_exposure=Decimal(-1),
        max_portfolio_heat=Decimal(0),
        max_leverage=Decimal(1),
        min_available_margin=Decimal(0),
    )

    try:
        limits.validate()
    except ValueError as exc:
        assert "max_gross_exposure" in str(exc)
    else:
        raise AssertionError("negative risk limit was accepted")
