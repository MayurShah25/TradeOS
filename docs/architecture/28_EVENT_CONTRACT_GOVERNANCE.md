# TradeOS Event Contract Governance

**Document:** `28_EVENT_CONTRACT_GOVERNANCE.md`  
**Version:** 0.1.0  
**Status:** Architecture Baseline  
**Scope:** Canonical event semantics, bounded event-driven workflows, idempotency, replay safety, loop prevention, and reasoning-trigger policy

---

## 1. Purpose

`24_EVENT_CONTRACTS.md` is the canonical source of truth for TradeOS event contracts.

This document records the governance rules established during the 01–25 consistency review so the event system remains useful, deterministic, auditable, and compatible with the TradeOS reasoning-efficiency principle.

> **Events communicate what happened. They do not create authority, and they do not automatically create AI work.**

---

# 2. Event vs Command

An event records a fact or material state change:

```text
order.filled
risk.rejected
trade.closed
```

A command requests an action:

```text
execute.order
cancel.order
reconcile.position
```

An event must never be interpreted as an implicit command or authorization.

---

# 3. Material Events Only

Consequential events should represent material domain, workflow, system, or governance changes.

TradeOS should not generate consequential event traffic for every internal thought, intermediate calculation, or routine agent activity.

Preferred:

```text
trade.proposed
risk.approved
authorization.issued
order.submitted
order.filled
position.updated
trade.closed
```

Avoid making transient internal reasoning steps part of the durable domain-event contract unless there is a specific audit or operational requirement.

---

# 4. Event-Driven Does Not Mean Agent-Driven

TradeOS may be event-driven without becoming an agent-to-agent conversation network.

Preferred:

```text
Event
  ↓
Deterministic Subscriber
  ↓
State / Calculation / Workflow Update
```

Reasoning is introduced only when the subscribed workflow determines that additional interpretation is valuable.

---

# 5. Explicit Event Routing

Every consequential event should have explicitly defined consumers.

Conceptually:

```text
EVENT
  ↓
DEFINED SUBSCRIBER
  ↓
DEFINED HANDLER
  ↓
DEFINED ACTION
```

A generic rule such as `any event → invoke an agent` is prohibited.

---

# 6. Reasoning Trigger Policy

An event may trigger an AI reasoning step only when:

1. The workflow explicitly requires the reasoning node.
2. A deterministic gate identifies a condition requiring interpretation.
3. A governed relevance policy determines that additional reasoning is materially useful.
4. A contradiction or uncertainty requires escalation.
5. Governance explicitly requires independent review.

Agent availability is not a sufficient trigger.

---

# 7. Example: Fill Event

```text
order.filled
     ↓
Position Service
     ↓
Portfolio Calculation
     ↓
Risk State Evaluation
```

These are deterministic operations.

A fill event should not automatically invoke multiple LLM agents.

If the resulting trade closure later warrants learning analysis:

```text
trade.closed
     ↓
Learning Relevance Check
     ↓
Only if useful
     ↓
Learning Agent
```

---

# 8. Idempotency

Every financially consequential event consumer must be idempotent.

The same `event_id` delivered more than once must not create duplicate financial effects.

Example:

```text
order.filled (event ABC)
        ↓
process
        ↓
order.filled (event ABC) again
        ↓
recognized as already processed
        ↓
no duplicate effect
```

---

# 9. At-Least-Once Delivery

The default distributed-system assumption is:

```text
AT-LEAST-ONCE DELIVERY
+
IDEMPOTENT CONSUMERS
```

Business-level exactly-once effects must be implemented through transactional/idempotent design rather than assumed from transport behavior.

---

# 10. Correlation and Causation

Every consequential workflow should preserve:

```text
correlation_id
causation_id
```

This allows TradeOS to reconstruct the chain:

```text
trade.proposed
      ↓
risk.evaluated
      ↓
risk.approved
      ↓
authorization.issued
      ↓
order.submitted
      ↓
order.filled
```

---

# 11. Loop Prevention

No event-driven workflow may create an unbounded feedback loop.

Workflows that can revisit a prior step must define:

```text
termination condition
maximum iterations
maximum duration
maximum relevant event depth
correlation boundary
```

Repeated events must not automatically re-enter the same workflow indefinitely.

---

# 12. Event Storm Prevention

Avoid cycles such as:

```text
position.updated
      ↓
risk.updated
      ↓
portfolio.updated
      ↓
risk.updated
      ↓
...
```

Where a derived update is sufficient, consumers should coalesce, debounce, or version-check updates according to the domain requirement.

---

# 13. Event Ordering

Consumers must not rely solely on network arrival order.

Where ordering matters, use appropriate combinations of:

```text
entity version
sequence number
occurred_at
causation_id
reconciliation
```

A late event must not overwrite newer authoritative state.

---

# 14. Event Payload Size

Events should contain the minimum sufficient information for the contract.

Prefer references to large or reusable objects:

```text
order_id
fill_id
instrument_id
quantity
price
occurred_at
```

rather than embedding entire portfolios, market histories, or agent transcripts.

This supports both system efficiency and reasoning-context efficiency.

---

# 15. Transactional Outbox

For material state changes that publish events, the preferred reliability pattern is:

```text
Database Transaction
      │
      ├── State Change
      │
      └── Outbox Event
              ↓
        Event Publisher
              ↓
           Event Bus
```

The state change and outbox record should commit atomically where the persistence architecture supports it.

---

# 16. Replay Safety

Historical event replay must never directly cause live execution.

```text
Historical Event Replay
       ↓
State Reconstruction / Analytics / Testing
```

not:

```text
Historical Event Replay
       ↓
Broker Order Submission
```

Live execution requires a fresh command, valid authorization, current state, and current safety checks.

---

# 17. Event Versioning

Every production event type must have explicit versioning.

Breaking semantic changes require a new major contract/version rather than silently changing an existing event's meaning.

Consumers should explicitly declare supported versions.

---

# 18. External Events

External broker, market-data, news, and web events are untrusted inputs.

They must pass validation and normalization before becoming trusted internal domain events.

External content cannot:

```text
change permissions
change system instructions
override risk
issue authorization
trigger unrestricted agent recursion
```

---

# 19. Event Security

Events must not expose:

- API keys
- Broker credentials
- Authentication tokens
- Secrets
- Unnecessary sensitive account data

Use references where appropriate.

---

# 20. Dead-Letter Handling

Unprocessable events should follow a controlled path:

```text
Event
 ↓
Retry Policy
 ↓
Dead Letter
 ↓
Investigation
 ↓
Correct / Replay
```

Dead-letter handling must not silently drop risk, execution, reconciliation, or audit events.

---

# 21. Event-to-Agent Budget

A workflow should define resource limits when reasoning can be triggered:

```text
max_agent_calls
max_iterations
max_duration
max_context_size
compute/token budget
```

Budgets are safety boundaries, not optimization objectives.

If required reasoning cannot complete within policy, the workflow should fail safely, abstain, degrade according to policy, or request review.

---

# 22. Event and Learning Interaction

Learning may analyze event histories to improve future workflow decisions.

The learning path is:

```text
events / outcomes
      ↓
learning observation
      ↓
pattern
      ↓
validation
      ↓
recommendation
      ↓
governance
      ↓
workflow improvement
```

Learning does not directly rewrite event history or grant execution authority.

---

# 23. Efficiency Principle

The event architecture must support the broader principle:

> **TradeOS should learn to think more efficiently so it can trade better.**

Therefore event-driven architecture should help TradeOS identify when reasoning is valuable rather than cause reasoning to occur by default.

---

# 24. Core Invariants

1. Events represent facts or material state changes.
2. Commands request actions.
3. Events do not create authority.
4. Consequential events have explicit consumers.
5. Events do not automatically invoke AI agents.
6. Financially consequential consumers are idempotent.
7. UNKNOWN execution state requires reconciliation.
8. Replay cannot create live execution.
9. Event-driven workflows are bounded and loop-protected.
10. External events cannot override TradeOS authority or safety rules.
11. Event payloads remain contract-sized and provenance-aware.
12. Additional reasoning is triggered only when its expected value justifies the cost and policy permits it.

---

## 25. Related Documents

- `22_DOMAIN_MODEL.md`
- `23_STATE_MACHINES.md`
- `24_EVENT_CONTRACTS.md`
- `25_AUTHORITY_AND_PERMISSION_MODEL.md`
- `26_REASONING_EFFICIENCY_AND_AGENT_ORCHESTRATION.md`
- `27_STATE_MACHINE_GOVERNANCE.md`

---

**TradeOS Event Principle**

> **Events should make the system more coordinated, not more complicated: communicate material facts, trigger only necessary work, and never create uncontrolled reasoning loops.**
