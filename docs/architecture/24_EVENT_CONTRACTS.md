# TradeOS Event Contracts

**Document:** `24_EVENT_CONTRACTS.md`  
**Version:** 0.1.0  
**Status:** Architecture Baseline  
**Scope:** Event envelope, event types, schemas, versioning, ordering, idempotency, delivery, provenance, and event governance

---

## 1. Purpose

This document defines the canonical event contract for TradeOS.

TradeOS is event-driven, but events are not merely log messages. Events are durable records of material facts or state transitions that may drive downstream workflows.

The governing principle is:

> **Events describe what happened; commands request what should happen.**

An event must never be interpreted as authorization unless its contract explicitly grants that meaning.

---

# 2. Event Design Principles

1. Events are immutable.
2. Events have stable identifiers.
3. Events are versioned.
4. Events identify producer and provenance.
5. Events distinguish occurrence time from processing time.
6. Events support idempotent consumption.
7. Events must not contain secrets.
8. Safety-critical events must be durable and auditable.
9. Event payloads use canonical domain objects.
10. Consumers must tolerate duplicate delivery.
11. UNKNOWN and failure states must be represented explicitly.
12. External events must be treated as untrusted input until validated.

---

# 3. Event vs Command

### Event

```text
Something happened.
```

Examples:

```text
order.filled
risk.rejected
position.updated
```

### Command

```text
Request that something happen.
```

Examples:

```text
execute.order
cancel.order
run.analysis
reconcile.position
```

Commands require authorization and validation. Events do not grant permissions by themselves.

---

# 4. Canonical Event Envelope

Every TradeOS event should use the following envelope:

```json
{
  "event_id": "evt_...",
  "event_type": "risk.approved",
  "event_version": "1.0",
  "occurred_at": "2026-01-01T10:00:00Z",
  "observed_at": "2026-01-01T10:00:00.100Z",
  "produced_at": "2026-01-01T10:00:00.110Z",
  "producer": "risk_engine",
  "environment": "paper",
  "workflow_id": "wf_...",
  "correlation_id": "corr_...",
  "causation_id": "evt_...",
  "schema_version": "1.0",
  "payload": {}
}
```

---

# 5. Event Identifiers

`event_id` must be globally unique.

Consumers should persist processed event IDs or use equivalent idempotency mechanisms.

Repeated delivery of the same event must not produce duplicate financial actions.

---

# 6. Correlation and Causation

### Correlation ID

Groups events belonging to one business workflow.

### Causation ID

Identifies the event or command that directly caused the current event.

Example:

```text
market.data.updated
        ↓
setup.detected
        ↓
trade.proposed
        ↓
risk.approved
        ↓
order.submitted
        ↓
order.filled
```

This creates a reconstructable event lineage.

---

# 7. Time Semantics

Events may contain:

```text
occurred_at
observed_at
produced_at
```

For market events, the real-world event time must be preserved.

Consumers must not substitute processing time for event time when it affects trading or backtesting correctness.

---

# 8. Event Categories

TradeOS events are grouped into:

```text
SYSTEM
MARKET
DATA
WORKFLOW
ANALYSIS
STRATEGY
PREDICTION
GOVERNANCE
RISK
EXECUTION
POSITION
TRADE
CONFIGURATION
LEARNING
MODEL
AGENT
SECURITY
RECONCILIATION
```

---

# 9. System Events

Examples:

```text
system.started
system.stopped
system.degraded
system.emergency
system.recovered
```

Payload should include system state and relevant version information.

---

# 10. Market Events

Examples:

```text
market.opened
market.closed
market.halted
market.resumed
instrument.enabled
instrument.disabled
```

Market status must originate from a trusted market/data source or governed configuration.

---

# 11. Data Events

Examples:

```text
market.data.updated
market.data.stale
market.data.invalid
market.data.anomaly_detected
provider.connected
provider.disconnected
```

A data event must identify provider/source and data quality where relevant.

---

# 12. Workflow Events

Examples:

```text
workflow.created
workflow.started
workflow.waiting
workflow.completed
workflow.rejected
workflow.failed
workflow.cancelled
```

Payload should reference workflow state and reason.

---

# 13. Analysis Events

Examples:

```text
analysis.requested
analysis.completed
analysis.abstained
analysis.failed
setup.detected
```

Analysis events contain references to structured outputs rather than treating free text as authoritative fact.

---

# 14. Strategy Events

Examples:

```text
strategy.proposal_created
strategy.review_requested
strategy.rejected
strategy.approved
strategy.paused
strategy.promoted
strategy.retired
```

Production strategy events must reference `strategy_version_id`.

---

# 15. Prediction Events

Examples:

```text
prediction.created
prediction.completed
prediction.abstained
prediction.invalidated
prediction.model_degraded
```

Prediction events must reference model version and uncertainty/calibration metadata where applicable.

---

# 16. Governance Events

Examples:

```text
critic.completed
portfolio.reviewed
approval.requested
approval.granted
approval.rejected
approval.expired
```

Governance events do not override hard Risk constraints.

---

# 17. Risk Events

Examples:

```text
risk.evaluated
risk.approved
risk.rejected
risk.review_required
risk.limit_reached
risk.state_changed
risk.halt_triggered
risk.halt_released
```

A `risk.approved` event must reference the exact Risk Decision and authorization context.

---

# 18. Execution Events

Examples:

```text
order_intent.created
order.validated
order.submitted
order.acknowledged
order.partially_filled
order.filled
order.cancel_requested
order.cancelled
order.rejected
order.expired
order.failed
order.unknown
```

An execution event must never claim a fill unless execution evidence supports it.

---

# 19. Position Events

Examples:

```text
position.opening
position.updated
position.reducing
position.closing
position.closed
position.reconciliation_required
position.mismatch
position.unknown
```

Position events should reference reconciliation evidence where broker state is involved.

---

# 20. Trade Events

Examples:

```text
trade.opened
trade.managed
trade.exit_requested
trade.closed
trade.invalidated
trade.outcome_recorded
```

A `trade.closed` event requires the applicable position-closure condition to have been satisfied.

---

# 21. Configuration Events

Examples:

```text
configuration.created
configuration.validated
configuration.approved
configuration.activated
configuration.deprecated
configuration.retired
configuration.rollback
configuration.drift_detected
```

Events must identify configuration version and hash.

---

# 22. Learning Events

Examples:

```text
learning.observation_recorded
learning.pattern_detected
learning.pattern_validated
learning.recommendation_created
learning.rule_approved
learning.rule_activated
learning.rule_expired
```

A learning event cannot activate a safety-critical behavior without the required governance process.

---

# 23. Model Events

Examples:

```text
model.created
model.validated
model.promoted
model.degraded
model.disabled
model.retired
```

Model events must reference immutable model versions.

---

# 24. Agent Events

Examples:

```text
agent.registered
agent.ready
agent.started
agent.completed
agent.abstained
agent.failed
agent.timeout
agent.degraded
agent.disabled
agent.circuit_breaker_triggered
```

Agent events must identify agent and prompt/configuration versions where relevant.

---

# 25. Security Events

Examples:

```text
security.permission_denied
security.authentication_failed
security.secret_access_failed
security.policy_violation
security.prompt_injection_detected
```

Security events must never expose secret values.

---

# 26. Reconciliation Events

Examples:

```text
reconciliation.started
reconciliation.completed
reconciliation.mismatch
reconciliation.resolved
reconciliation.failed
```

Reconciliation events should identify the internal and external state references involved.

---

# 27. Event Payload Rules

Payloads should:

- Use canonical domain objects.
- Use stable field names.
- Include explicit units.
- Include currency where monetary values exist.
- Include timestamps where time-sensitive.
- Include source references for external facts.
- Avoid duplicating mutable state unnecessarily.

---

# 28. Monetary Values

Money values must not rely on ambiguous floating-point semantics.

Recommended representation:

```text
amount
currency
```

The implementation should use a suitable decimal representation for financial calculations.

---

# 29. Quantities and Prices

Payloads must preserve market-specific precision.

Examples:

```text
quantity
price
tick_size
lot_size
contract_multiplier
```

Consumers must not silently round values outside instrument rules.

---

# 30. Schema Versioning

Every event type has an independent version.

Compatible changes may increment a minor version according to the schema governance policy.

Breaking changes require a new major version.

Consumers should explicitly declare supported versions.

---

# 31. Backward Compatibility

Event consumers should tolerate unknown optional fields.

Breaking changes should use a new event version rather than silently changing semantics.

Old events must remain interpretable for historical replay where practical.

---

# 32. Idempotent Consumption

Every consumer handling material events must be idempotent.

Example:

```text
order.filled
      ↓
Consumer processes event
      ↓
Database transaction commits
      ↓
Same event delivered again
      ↓
Consumer detects event_id already processed
      ↓
No duplicate action
```

---

# 33. Ordering

Events may arrive out of order because of distributed processing.

Consumers must use:

```text
occurred_at
sequence where available
causation_id
entity version
```

to determine whether an event is stale or requires reconciliation.

Financial execution must not depend solely on network arrival order.

---

# 34. Delivery Semantics

The initial architecture should prefer **at-least-once delivery with idempotent consumers** rather than assuming exactly-once delivery.

Exactly-once business effects must be achieved through transactional/idempotent design, not by trusting transport semantics alone.

---

# 35. Durable Event Storage

Material events should be durably stored before they are considered successfully committed where required by the workflow.

The implementation may use an event log, transactional outbox, or equivalent architecture.

---

# 36. Transactional Outbox

For transactional state changes that produce events:

```text
Domain State Change
        +
Outbox Event
        ↓
Same Transaction
        ↓
Event Publisher
        ↓
Event Bus
```

This prevents committed state changes from losing their corresponding events.

---

# 37. Event Replay

The system should support replay for:

- Debugging
- Recovery
- Analytics
- Testing
- Audit reconstruction

Replay must not automatically repeat real financial actions.

Execution commands must be separated from replayed historical events.

---

# 38. Event Retention

Retention policies should be explicit by category.

Financial, risk, execution, audit, and configuration events require durable historical retention appropriate to governance and legal requirements.

---

# 39. External Events

External events such as broker, news, and market data messages are untrusted inputs.

They must be:

```text
Received
 ↓
Authenticated / Validated
 ↓
Normalized
 ↓
Schema Checked
 ↓
Stored
 ↓
Published Internally
```

External text must not redefine TradeOS system instructions.

---

# 40. Event Security

Events must protect:

- API keys
- Broker credentials
- Authentication tokens
- Secrets
- Sensitive account information

Payloads should use references rather than secret values.

---

# 41. Event Observability

Monitor:

```text
publish rate
consumer lag
failure rate
retry rate
duplicate rate
out-of-order rate
dead-letter count
processing latency
```

Execution and risk events require especially strong monitoring.

---

# 42. Dead-Letter Handling

Events that cannot be processed should enter a controlled dead-letter path.

```text
Event
 ↓
Consumer Failure
 ↓
Retry Policy
 ↓
Dead Letter
 ↓
Investigation
 ↓
Recovery / Replay
```

A dead-lettered risk or execution event must not silently disappear.

---

# 43. Event Governance

Every production event type should define:

```text
event_type
version
producer
schema
required_fields
sensitivity
retention
consumers
ordering_requirements
idempotency_requirements
```

---

# 44. Event Contract Testing

Each event schema should have automated tests for:

- Required fields
- Types
- Version compatibility
- Invalid payloads
- Missing timestamps
- Invalid identifiers
- Duplicate handling
- Unknown optional fields
- Security-sensitive fields

---

# 45. Safety Invariants

The event system must enforce:

1. `risk.rejected` cannot cause an execution command.
2. `order.filled` cannot be emitted without execution evidence.
3. `position.closed` requires applicable reconciliation.
4. `configuration.activated` references a valid approved version.
5. Replayed historical events cannot create live orders.
6. Duplicate events cannot create duplicate financial actions.
7. Unknown execution state triggers reconciliation rather than assumption.

---

# 46. Example: Trade Approval Flow

```text
trade.proposed
      ↓
critic.completed
      ↓
portfolio.reviewed
      ↓
risk.evaluated
      ↓
risk.approved
      ↓
authorization.issued
      ↓
order_intent.created
      ↓
order.submitted
      ↓
order.filled
      ↓
position.updated
```

Every event is independently auditable.

---

# 47. Example: Unsafe Trade Flow

```text
trade.proposed
      ↓
risk.evaluated
      ↓
risk.rejected
      ↓
workflow.completed
```

No execution event should follow the rejection.

---

# 48. Implementation Rule

The event catalog and schemas should be represented as executable contracts and validated in CI.

No production component should invent ad-hoc event formats when a canonical event already exists.

---

## 49. Related Documents

- `22_DOMAIN_MODEL.md`
- `23_STATE_MACHINES.md`
- `25_AUTHORITY_AND_PERMISSION_MODEL.md`
- `04_SYSTEM_ARCHITECTURE.md`
- `12_EXECUTION_ARCHITECTURE.md`
- `20_AGENT_CONTRACTS.md`

---

**TradeOS Event Principle**

> **Record what happened precisely, propagate it safely, and never let an event become unintended authority.**
