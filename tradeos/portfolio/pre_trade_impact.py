"""Deterministic pre-trade portfolio impact calculations."""

from dataclasses import dataclass
from decimal import Decimal

from tradeos.execution import Order, OrderSide
from tradeos.portfolio.exposure import ExposureCalculator, ExposureSnapshot
from tradeos.portfolio.heat import PortfolioHeat
from tradeos.portfolio.open_orders import OpenOrderLedger
from tradeos.portfolio.position_ledger import PositionLedger


@dataclass(frozen=True, slots=True)
class PreTradeImpact:
    """Immutable projected portfolio impact of one order."""

    current_exposure: ExposureSnapshot
    projected_exposure: ExposureSnapshot
    current_heat: PortfolioHeat
    projected_heat: PortfolioHeat

    @property
    def exposure_change(self) -> Decimal:
        """Return projected minus current gross exposure."""
        return self.projected_exposure.gross - self.current_exposure.gross

    @property
    def heat_change(self) -> Decimal:
        """Return projected minus current portfolio heat."""
        return self.projected_heat.ratio - self.current_heat.ratio


class PreTradeImpactCalculator:
    """Project deterministic exposure and heat before an order is accepted."""

    @staticmethod
    def calculate(
        positions: PositionLedger,
        open_orders: OpenOrderLedger,
        prices: dict[str, Decimal],
        equity: Decimal,
        order: Order,
    ) -> PreTradeImpact:
        """Calculate current and projected gross exposure and portfolio heat."""
        current = ExposureCalculator.from_positions(positions, prices, open_orders)
        current_heat = PortfolioHeat.calculate(current, equity)

        projected_orders = OpenOrderLedger()
        for open_order in open_orders.orders():
            projected_orders.add(open_order)
        projected_orders.add(
            __import__("tradeos.portfolio.open_orders", fromlist=["OpenOrder"]).OpenOrder(
                order, __import__("tradeos.execution", fromlist=["OrderStatus"]).OrderStatus.ACCEPTED
            )
        )
        projected = ExposureCalculator.from_positions(positions, prices, projected_orders)
        projected_heat = PortfolioHeat.calculate(projected, equity)
        return PreTradeImpact(current, projected, current_heat, projected_heat)
