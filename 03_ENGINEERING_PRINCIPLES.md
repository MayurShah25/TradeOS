# TradeOS Engineering Principles

**Document:** 03_ENGINEERING_PRINCIPLES.md  
**Version:** 0.1.0  
**Status:** Approved Direction  
**Scope:** Engineering standards for TradeOS source code, infrastructure, agents, integrations, testing, and AI-assisted development.

---

## 1. Purpose

This document defines how TradeOS should be engineered.

The Project Vision defines **why TradeOS exists**.

The Design Principles define **how the system should behave architecturally**.

This document defines **how those principles should be implemented in software**.

These standards apply to:

- Human-written code
- AI-generated code
- Agents
- Strategies
- Models
- Market adapters
- Broker integrations
- Data pipelines
- Backtesting
- Paper trading
- Live trading
- Infrastructure
- Dashboard components

---

# 2. Documentation Before Implementation

No major subsystem should be implemented without an adequate specification.

Before coding a major component, define:

- Purpose
- Responsibilities
- Inputs
- Outputs
- Dependencies
- Permissions
- Failure behavior
- Testing approach
- Observability requirements
- Security considerations

Implementation should follow approved documentation.

---

# 3. Source Control Is Mandatory

GitHub is the source-control system for TradeOS.

All meaningful changes must be committed.

The repository should preserve:

- Code history
- Documentation history
- Architecture changes
- Strategy versions
- Configuration changes
- Agent contracts
- Experiment results

Do not develop important functionality exclusively outside version control.

---

# 4. Branching and Change Discipline

The repository should eventually use a controlled workflow such as:

```text
main
  │
  ├── feature/*
  ├── research/*
  ├── bugfix/*
  └── experiment/*
```

Research and experimental branches must not automatically become production code.

Production changes should be merged deliberately.

---

# 5. Small, Reviewable Changes

Prefer small changes over large uncontrolled rewrites.

Each meaningful change should have:

- Clear purpose
- Limited scope
- Tests where appropriate
- Documentation updates where required
- A useful commit message

Avoid modifying unrelated components while implementing a feature.

---

# 6. Modular Architecture

Major capabilities must be independently replaceable.

Examples:

```text
Broker Interface
      ↓
Zerodha Adapter

Broker Interface
      ↓
Dhan Adapter
```

and:

```text
Prediction Interface
      ↓
Model A

Prediction Interface
      ↓
Model B
```

The core system should depend on interfaces/contracts rather than vendor-specific implementations.

---

# 7. Interfaces Before Implementations

When a subsystem has multiple possible implementations, define its interface first.

Examples:

- `MarketDataProvider`
- `BrokerAdapter`
- `Strategy`
- `PredictionModel`
- `RiskEngine`
- `ExecutionEngine`
- `Agent`
- `BacktestEngine`

This makes replacement and testing easier.

---

# 8. Single Responsibility

Each module, class, function, and agent should have a clear responsibility.

Avoid components that simultaneously:

- Fetch data
- Calculate indicators
- Make strategy decisions
- Calculate risk
- Place orders
- Write reports

Separate those responsibilities.

---

# 9. Deterministic Code for Deterministic Work

Do not use an LLM when deterministic software can perform the task more reliably.

Use normal Python code for:

- Arithmetic
- Position sizing
- Risk calculations
- P&L
- Indicators
- Portfolio exposure
- Order validation
- Date/time calculations
- Data transformations
- Limit enforcement

Use AI for:

- Reasoning
- Interpretation
- Research
- Natural-language synthesis
- Hypothesis generation
- Explanation
- Qualitative comparison

---

# 10. Type Safety

Python code should use type hints consistently.

Prefer explicit data structures over loosely structured dictionaries when practical.

Use validated schemas/models for important boundaries.

Examples include:

- Pydantic models
- Typed objects
- Enums
- Dataclasses

Important trading objects should not rely on undocumented dictionary keys.

---

# 11. Configuration Over Hard-Coding

Operational parameters must not be scattered throughout source code.

Examples:

```text
risk_per_trade
maximum_daily_loss
maximum_drawdown
maximum_leverage
maximum_position_size
agent_timeout
maximum_agent_iterations
operating_mode
data_freshness_limit
```

Configuration should be:

- Centralized
- Validated
- Versioned
- Environment-aware
- Logged when changed

---

# 12. Safety-Critical Configuration

Safety-critical configuration requires additional protection.

Examples:

- Maximum risk
- Maximum leverage
- Kill-switch state
- Live trading authorization
- Maximum daily loss
- Maximum drawdown

Agents must not be able to arbitrarily modify these values.

---

# 13. Environment Separation

At minimum, TradeOS should distinguish:

```text
development
testing
research
paper
live
```

Credentials, databases, configuration, and broker access should be isolated as much as practical.

Code should not accidentally connect a development environment to live trading.

---

# 14. Live Trading Must Be Explicit

Live trading must require an explicit operating mode.

The system should never infer live authorization from:

- A successful broker connection
- A strategy passing a backtest
- A model becoming confident
- A user merely viewing the dashboard

Live execution must be intentionally enabled.

---

# 15. Secret Management

Never commit secrets to GitHub.

This includes:

- Broker API keys
- Broker secrets
- AWS credentials
- LLM API keys
- Database passwords
- Encryption keys
- Authentication tokens

Use environment variables or an appropriate secret-management solution.

Never place credentials directly in Python source code.

---

# 16. Error Handling

Errors must be handled explicitly.

Avoid broad exception handling that hides failures.

Bad:

```python
try:
    execute_trade()
except Exception:
    pass
```

Preferred behavior:

```text
Error
 ↓
Detect
 ↓
Log
 ↓
Classify
 ↓
Fail Safely
 ↓
Alert / Escalate
```

A failed execution component must never silently report success.

---

# 17. Fail-Safe Defaults

When uncertain, systems should default toward less risk.

Examples:

- Missing price → reject trade.
- Unknown position state → do not submit another order.
- Broker connection uncertain → pause execution.
- Risk calculation unavailable → reject trade.
- Data freshness unknown → reject affected strategy.
- Agent workflow stuck → terminate safely.

---

# 18. Logging

Logs must provide enough information to understand system behavior.

Important events should include:

- Timestamp
- Component
- Event
- Severity
- Instrument where applicable
- Strategy
- Agent
- Correlation/workflow ID
- Relevant identifiers
- Error details
- Outcome

Do not log secrets.

---

# 19. Structured Logging

Where possible, use structured logs rather than only free-form text.

Example:

```json
{
  "event": "risk_decision",
  "instrument": "XYZ",
  "decision": "REJECT",
  "reason": "daily_loss_limit",
  "risk_percent": 0.5,
  "workflow_id": "abc123"
}
```

This makes monitoring and debugging easier.

---

# 20. Correlation IDs

A trading workflow should have a unique identifier.

Example:

```text
workflow_id
trade_proposal_id
order_id
position_id
strategy_run_id
backtest_run_id
```

This allows the complete lifecycle of a decision to be traced.

---

# 21. Agent Engineering Standards

Every agent must have a formal contract defining:

- Purpose
- Inputs
- Outputs
- Context
- Tools
- Permissions
- Forbidden actions
- Timeout
- Retry behavior
- Failure behavior
- Escalation
- Token/context budget

Agents should communicate through structured contracts.

---

# 22. Agent Context Limits

Agents must not automatically receive the entire repository.

Context should be selected intentionally.

Example:

```text
Agent Request
     ↓
Context Resolver
     ↓
Required Documents
     ↓
Relevant Sections
     ↓
Structured Context
     ↓
Agent
```

Context limits should be measurable and testable.

---

# 23. Agent Loop Protection

Multi-agent workflows must have:

- Maximum iterations
- Maximum execution time
- Retry limits
- Termination conditions

The system must detect:

- Circular calls
- Duplicate requests
- Repeated outputs
- Unproductive debates
- Agent ping-pong

A workflow must terminate safely.

---

# 24. Token Budgeting

AI usage should have explicit budgets.

Track where practical:

- Input tokens
- Output tokens
- Number of model calls
- Agent iterations
- Cached context
- Estimated cost

Agents should not repeatedly request information they already received.

---

# 25. Caching

Cache information when:

- It is expensive to compute.
- It does not change frequently.
- Reuse is expected.
- Staleness can be controlled.

Cache entries should have:

- Creation time
- Expiration/freshness policy
- Source
- Version where applicable

Do not use stale cached market data for decisions where freshness is required.

---

# 26. Event-Driven Processing

Prefer event-driven execution over continuous polling where practical.

Potential events:

```text
market_data_updated
setup_detected
trade_proposed
risk_approved
order_submitted
order_filled
position_changed
risk_limit_reached
strategy_completed
trading_day_closed
```

Agents should run because something requires their work.

---

# 27. Testing Pyramid

TradeOS should use multiple testing levels.

```text
        System / E2E
             ▲
       Integration
             ▲
          Unit
```

### Unit Tests

For deterministic components such as:

- Position sizing
- Risk calculations
- Indicators
- Portfolio calculations

### Integration Tests

For:

- Broker adapters
- Database
- Market-data providers
- Agent orchestration

### End-to-End Tests

For:

- Complete trade workflows
- Paper trading
- Safety scenarios

---

# 28. Test Safety-Critical Components Aggressively

The following require especially strong test coverage:

- Risk engine
- Position sizing
- Order validation
- Kill switch
- Operating-mode enforcement
- Portfolio exposure
- Drawdown controls
- Broker execution state handling

A single incorrect calculation can have financial consequences.

---

# 29. Test With Failure Scenarios

Do not test only successful paths.

Test:

- Missing data
- Stale data
- Broker outage
- Duplicate order
- Partial fill
- Order rejection
- Incorrect position state
- Agent timeout
- Agent loop
- Database failure
- Network failure
- Invalid configuration
- Unexpected market conditions

---

# 30. Backtest Reproducibility

Every backtest must record:

- Dataset
- Data version
- Strategy version
- Parameters
- Configuration
- Costs
- Slippage
- Date range
- Market
- Timeframe
- Software version

The same inputs should produce reproducible results as far as practical.

---

# 31. Prevent Look-Ahead Bias

Backtesting code must not use information that would not have been available at the decision timestamp.

Special attention is required for:

- Future prices
- Future corporate actions
- Future fundamentals
- Revised data
- Survivorship bias
- Data leakage
- Feature engineering

---

# 32. Strategy Versioning

Each strategy must have a unique version.

Example:

```text
momentum_breakout
v1.0.0
v1.1.0
v2.0.0
```

Changes to entry, exit, risk, features, or model behavior should result in a new strategy version.

---

# 33. Model Versioning

Prediction models must be versioned separately from strategies.

Record:

- Model version
- Training dataset
- Features
- Training period
- Validation period
- Hyperparameters
- Evaluation metrics
- Deployment status

A model should never be silently replaced in production.

---

# 34. Data Contracts

Data entering important subsystems should conform to defined schemas.

Examples:

- Market tick
- OHLCV candle
- Instrument
- Order
- Position
- Trade proposal
- Risk decision
- Prediction
- Agent result

Invalid data should be rejected or quarantined.

---

# 35. Time Handling

Financial systems are extremely sensitive to time.

All important timestamps should be explicit and timezone-aware.

The system must distinguish:

- Exchange time
- Broker time
- UTC
- User/local time

Never rely on an implicit machine timezone for trading logic.

---

# 36. Monetary Precision

Financial calculations must use appropriate numerical representations.

Avoid careless floating-point calculations for money-sensitive operations.

Precision and rounding rules must be defined for:

- Prices
- Quantities
- P&L
- Fees
- Taxes
- Contract values
- Currency conversions

---

# 37. Market Adapter Standards

Each market adapter should expose a common interface while handling market-specific rules internally.

An adapter should provide, where applicable:

- Instruments
- Market data
- Trading sessions
- Contract specifications
- Tick sizes
- Lot sizes
- Order capabilities
- Position information
- Account information

---

# 38. Broker Adapter Standards

Broker-specific behavior belongs inside broker adapters.

The rest of TradeOS should not depend directly on a specific broker SDK.

Example:

```text
Execution Engine
      ↓
Broker Interface
      ↓
Zerodha Adapter
```

rather than:

```text
Strategy
   ↓
Zerodha SDK
```

---

# 39. Execution Safety

The execution layer must verify order state.

Do not assume:

```text
submit_order() == filled
```

The actual workflow is:

```text
Submit
 ↓
Broker Response
 ↓
Verify Status
 ↓
Confirm Fill
 ↓
Update Position
```

Unknown order state must be treated conservatively.

---

# 40. Idempotency

Critical operations should be designed to avoid unintended duplication.

For example, if an execution request is retried, the system should not accidentally create two trades.

Use appropriate unique identifiers and idempotency mechanisms.

---

# 41. Database Principles

The database should preserve the history needed for:

- Trades
- Orders
- Positions
- Market data references
- Agent decisions
- Risk decisions
- Strategy versions
- Model versions
- Backtest runs
- Learning outcomes
- Audit events

Important historical records should not be casually overwritten.

---

# 42. Immutable Audit Records

Where appropriate, important decision and execution records should be append-only.

If a correction is necessary:

```text
Original Record
      ↓
Correction Record
```

rather than silently rewriting history.

---

# 43. Observability

TradeOS should expose system health through:

- Logs
- Metrics
- Traces
- Agent status
- Workflow status
- Broker status
- Data freshness
- Risk state
- Execution state

The dashboard should make failures visible.

---

# 44. Monitoring

Monitor at least:

### System

- CPU
- Memory
- Disk
- Network
- Application health

### Trading

- Positions
- Orders
- P&L
- Exposure
- Drawdown
- Daily loss

### Data

- Feed status
- Data freshness
- Missing data
- Data anomalies

### AI

- Model calls
- Token usage
- Latency
- Errors
- Agent loops
- Cost

---

# 45. Security Boundaries

Security boundaries should exist between:

```text
Research
   ↓
Testing
   ↓
Paper
   ↓
Live
```

Live execution should require stronger authentication and authorization than research.

---

# 46. Codex / AI Coding Agent Rules

Codex and other AI coding assistants are implementation tools.

They must follow the repository architecture and documentation.

### Codex MUST:

1. Read relevant documentation before modifying a subsystem.
2. Follow `rules.md`.
3. Follow approved architecture documents.
4. Preserve existing interfaces unless a change is explicitly approved.
5. Add or update tests for meaningful behavior changes.
6. Explain significant architectural changes.
7. Keep changes focused.
8. Avoid unnecessary dependencies.
9. Avoid exposing secrets.
10. Update documentation when implementation changes documented behavior.
11. Preserve backward compatibility where required.
12. Report uncertainty rather than inventing requirements.

### Codex MUST NOT:

1. Modify global safety rules without explicit approval.
2. Remove or weaken risk controls.
3. Bypass the Risk Engine.
4. Enable live trading without explicit authorization.
5. Modify broker credentials.
6. Deploy an unvalidated strategy automatically.
7. Delete audit history to hide errors.
8. Disable logging to reduce noise.
9. Remove tests merely because they fail.
10. Rewrite unrelated modules unnecessarily.
11. Introduce hidden autonomous behavior.
12. silently change architecture.

---

# 47. AI-Generated Code Review

AI-generated code must be treated as untrusted until tested.

The fact that code was generated by an AI does not constitute validation.

For safety-critical components, review should include:

- Logic review
- Unit tests
- Edge cases
- Failure scenarios
- Security review
- Integration testing

---

# 48. Dependency Discipline

Do not add a dependency simply because it is convenient.

Before adding a package, consider:

- Is it necessary?
- Is it maintained?
- Is the license acceptable?
- Does it introduce security risk?
- Does it duplicate existing functionality?
- Does it increase operational complexity?

Dependencies should be documented when materially important.

---

# 49. API Integration Discipline

External APIs should be isolated behind adapters.

The system should handle:

- Rate limits
- Timeouts
- Authentication errors
- Connection errors
- Invalid responses
- Schema changes
- Retries
- Idempotency

External API failure must not automatically become a trading decision.

---

# 50. Research Code vs Production Code

Research code can be experimental.

Production code must meet stronger standards.

Research notebooks/scripts should not automatically become production services.

A promotion process should exist:

```text
Research
 ↓
Validated
 ↓
Refactored
 ↓
Tested
 ↓
Reviewed
 ↓
Production Candidate
```

---

# 51. No Magic Numbers

Financial and operational thresholds should not be hidden inside source code.

Bad:

```python
if loss > 5000:
    stop()
```

Preferred:

```python
if loss > config.maximum_daily_loss:
    stop()
```

---

# 52. Documentation as Code

If implementation changes behavior, update the relevant documentation.

Architecture, contracts, configuration, and workflows must remain synchronized with implementation.

Documentation drift should be treated as a defect.

---

# 53. Performance Before Optimization

Do not prematurely optimize.

First establish:

1. Correctness
2. Safety
3. Testability
4. Observability

Then optimize performance where measurement shows it is necessary.

---

# 54. Cost Awareness

AI and cloud costs must be observable.

The system should eventually track:

- Model usage
- Token consumption
- API calls
- Compute usage
- Storage
- Data-provider costs

Optimization should be based on measured usage rather than guesses.

---

# 55. Deployment Discipline

Deployments should be:

- Repeatable
- Versioned
- Reversible
- Observable

A deployment should identify:

- Software version
- Configuration version
- Database migration version
- Strategy versions
- Model versions

---

# 56. Rollback

Every production deployment should have a rollback strategy.

If a new version causes unexpected behavior:

```text
Detect
 ↓
Disable / Halt
 ↓
Rollback
 ↓
Verify
 ↓
Investigate
```

Do not continue trading merely because the system is "mostly working."

---

# 57. Code Quality Standard

Production code should favor:

- Clear names
- Small functions
- Explicit behavior
- Type hints
- Meaningful tests
- Minimal duplication
- Useful comments
- No dead code
- No hidden side effects

Code should be understandable to a developer who did not write it.

---

# 58. Final Engineering Standard

A component is not production-ready because it works under ideal conditions.

It is production-ready when it is:

```text
Correct
+
Safe
+
Tested
+
Observable
+
Reproducible
+
Documented
+
Versioned
+
Failure-Aware
```

---

# 59. Engineering Priority

When engineering concerns conflict, prioritize:

```text
1. Safety
2. Correctness
3. Data Integrity
4. Security
5. Reliability
6. Testability
7. Observability
8. Maintainability
9. Modularity
10. Performance
11. Cost
12. Convenience
```

---

## Related Documents

- `README.md`
- `rules.md`
- `docs/01_PROJECT_VISION.md`
- `docs/02_DESIGN_PRINCIPLES.md`
- `docs/04_SYSTEM_ARCHITECTURE.md`
- `docs/05_AGENT_ARCHITECTURE.md`
- `docs/06_DATA_ARCHITECTURE.md`
- `docs/08_RISK_MANAGEMENT.md`
- `docs/11_BACKTESTING_AND_VALIDATION.md`
- `docs/20_AGENT_CONTRACTS.md`
- `docs/21_CONFIGURATION.md`
- `docs/23_CODEX_IMPLEMENTATION_PLAN.md`
- `decisions/ARCHITECTURAL_DECISIONS.md`

---

## Version History

| Version | Status | Description |
|---|---|---|
| 0.1.0 | Approved Direction | Initial engineering principles for TradeOS |

---

> **Build carefully. Test aggressively. Fail safely. Never allow convenience to weaken financial safety.**
