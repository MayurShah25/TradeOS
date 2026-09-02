"""Deterministic portfolio heat calculations."""

from dataclasses import dataclass
from decimal import Decimal

from tradeos.portfolio.exposure import ExposureSnapshot


@dataclass(frozen=True, slots=True)
class PortfolioHeat:
    """Immutable portfolio heat as exposure divided by equity."""

    gross_exposure: Decimal
    equity: Decimal
    ratio: Decimal

    @classmethod
    def calculate(cls, exposure: ExposureSnapshot, equity: Decimal) -> "PortfolioHeat":
        """Calculate gross exposure as a fraction of positive equity."""
        if equity <= 0:
            raise ValueError("equity must be positive")
        ratio = exposure.gross / equity
        return cls(exposure.gross, equity, ratio)
