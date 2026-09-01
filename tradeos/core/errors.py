"""Application error hierarchy for TradeOS."""


class TradeOSError(Exception):
    """Base exception for expected TradeOS application failures."""


class ConfigurationError(TradeOSError):
    """Raised when application configuration is invalid."""


class ContractError(TradeOSError):
    """Raised when a command or event violates its contract."""


class StateTransitionError(TradeOSError):
    """Raised when a state transition cannot be applied."""


class PersistenceError(TradeOSError):
    """Raised when a persistence operation cannot be completed."""


class AuthorizationError(TradeOSError):
    """Raised when a requested operation lacks required authority."""
