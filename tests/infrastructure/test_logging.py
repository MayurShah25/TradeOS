import json

import pytest

from tradeos.infrastructure.logging import audit_record, structured_fields


def test_audit_record_contains_required_fields() -> None:
    record = json.loads(
        audit_record(
            event_type="risk.decision",
            action="evaluate",
            actor="risk-engine",
            correlation_id="corr-1",
            outcome="approved",
            decision_id="decision-1",
        )
    )

    assert record["event_type"] == "risk.decision"
    assert record["action"] == "evaluate"
    assert record["actor"] == "risk-engine"
    assert record["correlation_id"] == "corr-1"
    assert record["outcome"] == "approved"
    assert record["decision_id"] == "decision-1"
    assert record["timestamp"]


def test_audit_record_requires_identity_fields() -> None:
    with pytest.raises(ValueError, match="audit identity fields are required"):
        audit_record(
            event_type="",
            action="evaluate",
            actor="risk-engine",
            correlation_id="corr-1",
            outcome="approved",
        )


def test_structured_fields_reject_reserved_log_record_names() -> None:
    with pytest.raises(ValueError, match="Reserved logging fields"):
        structured_fields(message="unsafe")
