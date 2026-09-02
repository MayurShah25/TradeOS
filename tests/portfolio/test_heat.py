from decimal import Decimal

import pytest

from tradeos.portfolio.exposure import ExposureSnapshot
from tradeos.portfolio.heat import PortfolioHeat


def test_portfolio_heat_is_gross_exposure_over_equity() -> None:
    heat = PortfolioHeat.calculate(ExposureSnapshot(Decimal(2500), Decimal(500)), Decimal(10000))
    assert heat.gross_exposure == Decimal(2500)
    assert heat.equity == Decimal(10000)
    assert heat.ratio == Decimal("0.25")


def test_portfolio_heat_requires_positive_equity() -> None:
    with pytest.raises(ValueError, match="positive"):
        PortfolioHeat.calculate(ExposureSnapshot(Decimal(100), Decimal(100)), Decimal(0))
