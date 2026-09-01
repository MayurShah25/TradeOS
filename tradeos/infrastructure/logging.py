"""Structured logging foundation for TradeOS."""

import datetime
import json
import logging
from typing import Any


_RESERVED = set(logging.LogRecord(None, 0, "", 0, "", (), None).__dict__) | {"message"}


def configure_logging(level: str = "INFO") -> None:
    """Configure the process logger with a deterministic structured formatter."""
    logging.basicConfig(
        level=level.upper(),
        format="%(message)s",
    )


def get_logger(name: str) -> logging.Logger:
    """Return a namespaced logger."""
    return logging.getLogger(name)


def structured_fields(**fields: Any) -> dict[str, Any]:
    """Build safe structured fields while rejecting reserved LogRecord names."""
    invalid = _RESERVED.intersection(fields)
    if invalid:
        raise ValueError(f"Reserved logging fields: {sorted(invalid)}")
    return fields


def audit_record(
    *,
    event_type: str,
    action: str,
    actor: str,
    correlation_id: str,
    outcome: str,
    **fields: Any,
) -> str:
    """Serialize a minimal audit record without secrets or credentials."""
    if not all(value.strip() for value in (event_type, action, actor, correlation_id, outcome)):
        raise ValueError("audit identity fields are required")

    record = {
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "event_type": event_type,
        "action": action,
        "actor": actor,
        "correlation_id": correlation_id,
        "outcome": outcome,
        **structured_fields(**fields),
    }
    return json.dumps(record, sort_keys=True, default=str)
