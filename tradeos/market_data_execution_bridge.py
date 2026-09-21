"""Deterministic bridge from persisted paper market data to paper execution."""

from datetime import datetime, timedelta

from tradeos.execution import Order, PaperTradingResult, PaperTradingRun, PaperTradingSession
from tradeos.market_data import (
    PaperMarketDataFreshnessPolicy,
    validate_paper_market_data,
)
from tradeos.market_data_repository import PaperMarketDataRepository
from tradeos.market_data_stream import PaperMarketDataStream
from tradeos.portfolio import PortfolioRiskLimits, PortfolioState, RiskContextBuilder


class PaperMarketDataExecutionBridge:
    """Connect one ordered, persisted market observation to governed paper execution."""

    def __init__(
        self,
        *,
        repository: PaperMarketDataRepository,
        stream: PaperMarketDataStream,
        session: PaperTradingSession,
    ) -> None:
        self._repository = repository
        self._stream = stream
        self._session = session

    def execute_latest(
        self,
        *,
        authorization_id: str,
        risk_decision_id: str,
        order: Order,
        portfolio: PortfolioState,
        limits: PortfolioRiskLimits,
        now: datetime,
        max_market_data_age: timedelta,
        run: PaperTradingRun | None = None,
    ) -> PaperTradingResult:
        """Execute an order using only the stream’s latest persisted observation."""
        snapshot = self._stream.latest()
        if snapshot is None:
            raise ValueError("no market-data snapshot is available")

        persisted = self._repository.get(
            instrument_id=snapshot.instrument_id,
            source_id=snapshot.source_id,
            observed_at=snapshot.observed_at,
        )
        if persisted != snapshot:
            raise ValueError("latest market-data snapshot is not persisted")

        policy = self._freshness_policy(max_market_data_age)
        validate_paper_market_data(
            snapshot,
            instrument_id=order.instrument_id,
            observed_at=now,
            policy=policy,
        )

        context = RiskContextBuilder.build(
            portfolio,
            {snapshot.instrument_id: snapshot.price},
            now,
            max_market_data_age,
        )
        return self._session.execute(
            authorization_id,
            risk_decision_id,
            order,
            context,
            limits,
            {snapshot.instrument_id: snapshot.price},
            now,
            run=run,
        )

    @staticmethod
    def _freshness_policy(
        max_market_data_age: timedelta,
    ) -> PaperMarketDataFreshnessPolicy:
        if max_market_data_age < timedelta(0):
            raise ValueError("max_market_data_age cannot be negative")
        max_age_seconds = int(max_market_data_age.total_seconds())
        return PaperMarketDataFreshnessPolicy(max_age_seconds=max_age_seconds)