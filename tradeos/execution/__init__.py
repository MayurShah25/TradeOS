"""Paper-safe execution boundary for TradeOS."""

from .audit import AuditEvent, AuditEventType, AuditTrail
from .authorization import (
    AuthorizationLedger,
    AuthorizationStatus,
    ExecutionAuthorization,
    ExecutionAuthorizationPolicy,
    OperatingMode,
)
from .authorized_gateway import (
    AuthorizedExecutionGateway,
    ExecutionGatewayResult,
    ExecutionOutcomeUnknownError,
)
from .lifecycle import ReconciliationStatus
from .models import Order, OrderSide, OrderStatus, OrderType
from .paper_broker import PaperBroker
from .paper_session import PaperTradingResult, PaperTradingSession
from .ports import BrokerExecutionPort, PaperTradingPersistencePort
from .reconciliation import PaperReconciliationResult, PaperTradingReconciliation
from .recovery import PaperRunRecoveryAssessment, PaperTradingRecovery
from .run_registry import PaperRunRegistry
from .run_state import PaperRunStatus, PaperTradingRun

__all__ = [
    "AuditEvent",
    "AuditEventType",
    "AuditTrail",
    "AuthorizationLedger",
    "AuthorizationStatus",
    "AuthorizedExecutionGateway",
    "BrokerExecutionPort",
    "ExecutionAuthorization",
    "ExecutionAuthorizationPolicy",
    "ExecutionGatewayResult",
    "ExecutionOutcomeUnknownError",
    "OperatingMode",
    "Order",
    "OrderSide",
    "OrderStatus",
    "OrderType",
    "PaperBroker",
    "PaperReconciliationResult",
    "PaperRunRecoveryAssessment",
    "PaperRunRegistry",
    "PaperRunStatus",
    "PaperTradingPersistencePort",
    "PaperTradingReconciliation",
    "PaperTradingRecovery",
    "PaperTradingResult",
    "PaperTradingRun",
    "PaperTradingSession",
    "ReconciliationStatus",
]
