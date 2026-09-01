# TradeOS State Machine Governance

**Document:** `27_STATE_MACHINE_GOVERNANCE.md`  
**Version:** 0.2.0  
**Status:** Architecture Baseline  
**Scope:** Canonical state-machine governance rules, deterministic transition validation, evidence requirements, concurrency, reconciliation, event emission, recovery, and transition safety

---

## 1. Purpose

TradeOS treats state as operational control, not descriptive metadata. A state determines which actions are legal, which transitions are possible, and which safeguards must apply.

`23_STATE_MACHINES.md` is the canonical source of truth for lifecycle states and legal transitions.

This document records the governance rules that must be enforced by implementation.

---

# 2. Core Rules

### Rule 1 — Canonical State Source

`23_STATE_MACHINES.md` defines canonical lifecycle states and legal transitions. Other architecture documents may explain behavior but must not create competing state vocabularies.

### Rule 2 — Explicit Transition Authority

Every material transition has an authoritative subsystem. Agents may request or recommend transitions but cannot arbitrarily mutate safety-critical state.

### Rule 3 — Deterministic Validation

Every material transition must pass deterministic validation of:

```text
current state
requested transition
authority
preconditions
required evidence
operating mode
configuration
entity version / concurrency condition
```

### Rule 4 — Evidence Before Fact

A transition is valid only when its required evidence exists.

Examples:

```text
ORDER → FILLED
requires execution/fill evidence

POSITION → CLOSED
requires applicable closure/reconciliation evidence

STRATEGY → PRODUCTION
requires governed approval
```

### Rule 5 — UNKNOWN Is First-Class

`UNKNOWN` is not equivalent to `FAILED`.

An unknown external state requires reconciliation before a consequential assumption or duplicate financial action is made.

### Rule 6 — Material Transitions Emit Events

Material state transitions produce canonical versioned events defined by `24_EVENT_CONTRACTS.md`.

The transition and its required durable event record should be committed atomically where the persistence architecture supports it.

### Rule 7 — History Is Preserved

Material state transitions must remain auditable. Corrections create explicit corrective history rather than silently rewriting prior state.

### Rule 8 — State Is Versioned for Concurrency

Material state must expose a version, sequence, or equivalent concurrency token where concurrent updates are possible.

A transition validated against stale state must be rejected or revalidated rather than silently overwriting newer state.

### Rule 9 — Transition Effects Are Idempotent

Retries or duplicate transition requests must not create duplicate financial or governance effects.

A transition request should have a stable idempotency key or equivalent uniqueness protection where duplicate delivery is possible.

### Rule 10 — Events Do Not Grant Authority

A state-transition event communicates an accepted fact. It does not independently authorize a new privileged action.

Downstream actions must perform their own authority and current-state checks.

---

# 3. Canonical State Transition Pipeline

```text
Current State
      ↓
Requested Transition
      ↓
State Machine
      ↓
Authority Check
      ↓
Precondition Check
      ↓
Evidence Check
      ↓
Concurrency / Version Check
      ↓
State Change
      ↓
Canonical Event
      ↓
Downstream Workflow
```

Invalid transitions terminate at validation and must not mutate state.

Where a state change and canonical event are required to represent one material fact, implementation should use a transactional boundary or equivalent consistency mechanism.

---

# 4. Critical UNKNOWN Rule

For external execution state:

```text
Submission
   ↓
Timeout / Ambiguous Response
   ↓
UNKNOWN
   ↓
Reconciliation
   ↓
Resolved State
```

The system must not infer:

```text
UNKNOWN → FAILED → RESUBMIT
```

without authoritative evidence and policy permitting that transition.

This rule exists to prevent duplicate orders and unintended exposure.

While execution state is unresolved, the system must not treat the unresolved state as permission to create another financially consequential action.

---

# 5. Critical Execution State Chain

```text
Trade Proposal
      ↓
Risk Decision
      ↓
Execution Authorization
      ↓
Order Intent
      ↓
Order
      ↓
Fill
      ↓
Position
      ↓
Trade
```

Each stage has its own state and evidence requirements. A later state cannot be manufactured merely because an earlier intention existed.

The existence of an upstream approval or intent does not substitute for downstream execution evidence.

---

# 6. Immutable Decision Records

The following are treated as immutable historical decisions or evidence records after issuance/creation, subject to explicit corrective records:

```text
Risk Decision
Execution Authorization
Order Intent
Order Submission Record
Fill
State Transition Record
Configuration Version
Learning Observation
```

Operational current-state projections may change, but their history remains auditable.

Corrections must identify what was corrected, why, by whom or which subsystem, and what evidence supported the correction.

---

# 7. Authorization Reuse

Live execution authorization is single-use by default.

A reusable authorization requires an explicit policy that defines:

```text
scope
maximum uses
validity window
permitted changes
consumption semantics
```

An authorization must never be unintentionally reusable merely because the record remains present.

Authorization consumption must be protected against concurrent workers attempting to use the same authorization.

---

# 8. Agent Boundary

AI agents must not perform arbitrary assignments such as:

```text
order.status = FILLED
position.status = CLOSED
strategy.status = PRODUCTION
```

Instead, agents may submit structured requests to the appropriate deterministic subsystem, which validates and applies the transition.

An agent response is evidence or a request, not state authority, unless the agent is explicitly the authoritative component for that non-safety-critical lifecycle domain.

---

# 9. Concurrency

State transitions must be protected against races.

For example, two workers must not both consume the same single-use authorization.

Implementation may use transactions, optimistic locking, unique constraints, compare-and-swap semantics, or equivalent mechanisms.

The authoritative service must detect stale versions before applying a material transition.

---

# 10. Reconciliation Authority

When internal state conflicts with an external financial system, reconciliation must establish the authoritative external fact before consequential state is resolved.

```text
Internal State
      +
External State
      ↓
Reconciliation
      ↓
Evidence-backed Resolution
      ↓
State Transition
```

Reconciliation itself does not grant execution authority. A resolved state must still pass normal transition and safety rules.

---

# 11. Recovery

Recovery follows:

```text
Failure / Unknown
      ↓
Assess Current State
      ↓
Reconcile if Required
      ↓
Revalidate Safety
      ↓
Resume / Block / Escalate
```

Process restart alone is never considered domain-state recovery.

Recovery must use current state rather than replaying assumptions from an earlier workflow attempt.

---

# 12. Stale State and Revalidation

A state or approval may become stale when material inputs change.

Examples include:

```text
market state changed
account state changed
portfolio exposure changed
risk limits changed
configuration changed
operating mode changed
required evidence changed
external state changed
```

A stale state must not silently authorize a consequential transition. The applicable workflow must revalidate or explicitly reject the transition according to policy.

---

# 13. Transition and Event Ordering

Consumers must not infer authoritative state solely from event arrival order.

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

# 14. Testing Requirements

State-machine tests must cover:

- Every legal transition
- Every illegal transition
- Terminal-state protection
- UNKNOWN behavior
- Required evidence
- Authorization expiry
- Authorization reuse
- Concurrent transitions
- Stale-version rejection
- Retry and idempotency behavior
- Recovery behavior
- Reconciliation behavior
- Kill-switch behavior
- Permission enforcement
- Event emission
- Event/state consistency

---

# 15. Implementation Contract

The implementation must expose deterministic transition operations rather than allowing callers to mutate safety-critical state directly.

Conceptually:

```text
Transition Request
      ↓
Deterministic Validator
      ↓
Authorized State Mutation
      ↓
Transition Record
      ↓
Canonical Event
```

The implementation should reject direct writes that bypass the transition contract.

---

# 16. Core Invariants

The following must remain true:

1. `23_STATE_MACHINES.md` remains the canonical lifecycle vocabulary.
2. Every material transition has an authoritative subsystem.
3. Invalid transitions do not mutate state.
4. Required evidence exists before a transition is accepted.
5. `UNKNOWN` is never silently treated as `FAILED`.
6. Material state history is preserved.
7. Material transitions are versioned and auditable.
8. Concurrent workers cannot accidentally apply the same single-use transition twice.
9. Stale state cannot silently authorize material exposure.
10. State changes and their required canonical events use an appropriate consistency boundary.
11. Events communicate facts but do not create authority.
12. Recovery begins with assessment and reconciliation where required, not process restart assumptions.
13. AI agents cannot directly mutate safety-critical state.
14. Replayed or retried requests cannot create duplicate financial effects.

---

## 17. Related Documents

- `22_DOMAIN_MODEL.md`
- `23_STATE_MACHINES.md`
- `24_EVENT_CONTRACTS.md`
- `25_AUTHORITY_AND_PERMISSION_MODEL.md`
- `26_REASONING_EFFICIENCY_AND_AGENT_ORCHESTRATION.md`
- `12_EXECUTION_ARCHITECTURE.md`
- `08_RISK_MANAGEMENT.md`

---

**TradeOS State Principle**

> **A state change is a governed fact: it requires legal authority, valid evidence, current state, and an auditable transition.**
