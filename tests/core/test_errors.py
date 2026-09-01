from tradeos.core.errors import (
    AuthorizationError,
    ConfigurationError,
    ContractError,
    PersistenceError,
    StateTransitionError,
    TradeOSError,
)


def test_application_errors_share_tradeos_base() -> None:
    error_types = (
        ConfigurationError,
        ContractError,
        StateTransitionError,
        PersistenceError,
        AuthorizationError,
    )

    assert all(issubclass(error_type, TradeOSError) for error_type in error_types)


def test_application_errors_preserve_message() -> None:
    error = PersistenceError("database unavailable")

    assert str(error) == "database unavailable"
