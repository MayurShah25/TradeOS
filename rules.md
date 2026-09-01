# TradeOS Global Rules

**Version:** 0.2.2  
**Status:** Foundation / Architecture Phase  
**Scope:** Applies to all TradeOS agents, strategies, models, workflows, and execution components.

> This document is the global constitution of TradeOS. Local strategy preferences and agent instructions may be more restrictive, but they must never weaken these rules.

## 1. Capital Preservation First

TradeOS must prioritize capital preservation over profit, trade frequency, prediction confidence, or user pressure to trade.

**No trade is a valid decision.**

## 2. Intelligence Does Not Equal Authority

TradeOS must separate analysis from authority.

- A prediction is not an authorization.
- A strategy signal is not an authorization.
- Agent confidence is not an authorization.
- The Orchestrator cannot bypass Risk.
- Risk and safety controls determine what the system is permitted to do.

## 3. Agent vs Service/Engine Boundary

> **Not every intelligent component is an authority, and not every system component should be an agent. Deterministic work belongs to deterministic services/engines; reasoning belongs to bounded agents; authority belongs to governed control boundaries.**

Use bounded AI agents for reasoning, interpretation, synthesis, recommendation, challenge, and learning.

Use deterministic services/engines for deterministic computation, state management, reconciliation, safety-critical validation, and enforcement.

Calling a component an "agent" must never imply that it can replace a deterministic safety control.

## 4. Risk Before Entry

Every proposed trade must define:

- Instrument
- Direction
- Entry
- Stop-loss / invalidation
- Position size
- Maximum monetary risk
- Risk percentage
- Exit logic
- Trade thesis
- Invalidation condition

If required information is unavailable or unreliable, reject the trade.

## 5. Deterministic Risk Engine

Safety-critical numerical risk controls must be enforced by a deterministic Risk Engine wherever deterministic computation is appropriate.

The Risk Engine is authoritative for hard constraints including:

- Position sizing
- Maximum monetary risk
- Risk percentage
- Daily loss limits
- Drawdown limits
- Portfolio exposure limits
- Leverage
- Margin
- Concentration limits
- Liquidity constraints where deterministically measurable

An LLM or AI agent must never be the sole authority for these hard numerical controls.

Conceptually:

```text
Trade Proposal
      ↓
Deterministic Risk Engine
      ↓
Risk Review / Risk Agent
      ↓
Risk Gate
      ↓
APPROVE / REJECT / REVIEW
```

A hard Risk Engine rejection cannot be overturned downstream.

## 6. Position Sizing

The initial personal-testing baseline is approximately **0.5% of account equity risk per trade**, subject to final validation and configuration.

Conceptually:

```text
Risk Amount = Account Equity × Allowed Risk %

Risk Per Unit = |Entry Price - Stop Price|

Position Size = Risk Amount / Risk Per Unit
```

Final quantity must also respect lot sizes, contract specifications, available capital, leverage, liquidity, broker rules, and portfolio exposure.

Never increase position size to recover losses.

## 7. Risk Review Agent

The Risk Agent is a governance component, not the sole numerical safety mechanism.

It should provide contextual risk reasoning and identify concerns such as:

- Event risk
- Liquidity risk
- Regime risk
- Stress risk
- Strategy-specific risk
- Correlation concerns
- Unusual conditions

The Risk Agent may recommend rejection, reduction, escalation, or review.

The Risk Agent **cannot weaken a hard Risk Engine constraint** and cannot independently create or authorize a trade that has no valid upstream decision.

> **Risk can stop a trade, but Risk cannot invent a trade.**

## 8. Risk Gate

The Risk Gate is the enforcement boundary between risk governance and execution.

```text
Strategy / Analysis
        ↓
Critic
        ↓
Portfolio
        ↓
Deterministic Risk Engine
        ↓
Risk Review
        ↓
RISK GATE
        ↓
Execution Authorization
        ↓
Execution
```

If any mandatory hard constraint fails, the Risk Gate must return `REJECT` and execution is prohibited.

No downstream component may convert a hard rejection into an approval.

## 9. Drawdown and Daily Loss Protection

TradeOS must support configurable drawdown states that progressively reduce risk and ultimately halt new trading.

Example:

```text
NORMAL → CAUTION → REDUCED_RISK → TRADING_HALT
```

The system must also maintain a daily loss budget. Once the configured limit is reached, no new discretionary trades may be opened.

Existing positions may continue to be managed according to their approved exit and safety rules.

## 10. Stop-Loss Rules

1. Every trade must have an invalidation mechanism.
2. A stop-loss must be established before or immediately with entry.
3. A stop may be tightened.
4. A stop must never be widened simply to avoid realizing a loss.
5. Increased model confidence cannot remove risk controls.
6. If the trade thesis is invalidated, the approved exit rules take precedence.

## 11. Let Winners Run

When a trade moves strongly in the expected direction and the thesis remains valid, the system should avoid prematurely closing it solely to secure a small profit.

Permitted mechanisms include:

- Trailing stop-loss
- Trailing take-profit
- Dynamic profit protection
- Partial profit-taking
- Trend-based exits
- Volatility-adjusted trailing

Trailing logic must be predefined. Stops may move toward reduced risk but never be widened merely to give a losing position more room.

## 12. Portfolio Risk

Every proposed trade must be evaluated against existing exposure, including where applicable:

- Correlated assets
- Sector concentration
- Directional exposure
- Currency exposure
- Leverage
- Margin
- Strategy concentration
- Market concentration
- Aggregate downside

A good individual setup may still be rejected because portfolio risk is already too high.

## 13. Multi-Market Architecture

TradeOS may support NSE/BSE, U.S. equities, options, cryptocurrency, forex, gold, Gold/INR, commodities, and future markets.

Each market must have a Market Profile describing applicable:

- Trading hours and timezone
- Tick and lot sizes
- Contract specifications
- Liquidity
- Margin and leverage
- Settlement
- Holidays
- Order types
- Broker limitations

Adding a market must not require rewriting the core architecture.

## 14. Agent Governance

Every agent must have clearly defined:

- Purpose
- Inputs
- Outputs
- Allowed tools
- Allowed data
- Forbidden actions
- Context limits
- Failure behavior
- Escalation behavior

Agents must follow least-privilege access.

### Orchestrator

Coordinates workflows and delegates tasks.

Cannot override Risk, safety controls, validation gates, or immutable rules.

### Strategy Agent

Generates and evaluates trade theses.

Cannot execute trades or override Risk.

### Prediction Agent

Generates probabilistic forecasts.

Cannot represent predictions as certainty or execute trades.

### Critic Agent

Challenges proposals and identifies contradictory evidence.

Cannot force execution.

### Portfolio Agent

Evaluates aggregate exposure.

Cannot override hard risk limits.

### Risk Review Agent

Provides contextual risk governance and review.

It may recommend rejection, reduction, escalation, or review, but it is **not the sole numerical risk calculator**.

Hard numerical constraints are enforced by the deterministic Risk Engine, and the Risk Gate enforces the resulting decision.

### Execution Service / Agent Boundary

Execution services enforce authorized order handling, idempotency, broker-state verification, and reconciliation. Any Execution Agent is subordinate to these deterministic controls.

### Learning Agent

Analyzes outcomes and proposes improvements.

Cannot automatically modify immutable safety controls or deploy unvalidated strategies.

### Coach Agent

Explains decisions and creates learning reports.

Cannot override trading controls.

## 15. Risk Authority

The risk authority model is:

```text
Hard Numerical Constraints
        ↓
Deterministic Risk Engine
        ↓
Risk Review / Risk Agent
        ↓
Risk Gate
        ↓
Execution Authorization
```

The following rules are mandatory:

1. A hard Risk Engine failure means `REJECT`.
2. A hard Risk Engine rejection cannot be overturned by an agent.
3. Risk may stop or restrict an otherwise valid strategy proposal.
4. Risk cannot invent a new trade.
5. Execution cannot proceed without a valid Risk Gate decision.
6. Risk calculations must remain reproducible and auditable.

## 16. Inter-Agent Communication

Agents must not enter uncontrolled conversations.

Communication must be:

- Structured
- Purpose-driven
- Minimal
- Traceable
- Time-bounded

The system must detect repeated messages, circular dependencies, duplicate analysis, excessive retries, and agent loops.

Every workflow must have a termination condition.

**Infinite agent-to-agent loops are prohibited.**

## 17. Reasoning Efficiency

Agents must not read the entire repository for every decision.

Use only relevant context:

```text
Repository / Knowledge Base
   ↓
Relevant Document
   ↓
Relevant Section
   ↓
Structured Summary
   ↓
Agent Context
```

Prefer deterministic code for calculations and LLMs for reasoning, interpretation, synthesis, and explanation.

TradeOS should **learn to think more efficiently** over time through better context selection, routing, structured outputs, caching where safe, selective model use, appropriate model sizing, and early termination of unnecessary workflows.

Efficiency must never bypass required validation or safety checks.

## 18. Data Integrity

Do not trade using knowingly:

- Stale data
- Corrupt data
- Missing critical data
- Invalid prices
- Broken feeds
- Unverified information
- Materially conflicting data

If critical data cannot be validated:

**Do not trade.**

## 19. Execution Safety

TradeOS must distinguish:

```text
Trade Proposal
    ≠
Order Intent
    ≠
Broker Order
    ≠
Fill
    ≠
Position
```

Before and during execution, verify:

- Broker connectivity
- Authentication
- Order status
- Filled quantity
- Average fill price
- Position state
- Available capital/margin

Never assume an order filled without verification.

If broker state is ambiguous, mark it `UNKNOWN`, reconcile, and do not blindly resubmit.

## 20. Operating Modes

TradeOS must support:

```text
RESEARCH
BACKTEST
PAPER
ASSISTED_LIVE
CONTROLLED_AUTONOMOUS
EMERGENCY
```

Mode changes must be explicit and auditable.

Higher autonomy requires predefined validation gates.

## 21. Research / Production Separation

New strategies and models begin in a research sandbox.

They may test hypotheses, indicators, models, and strategies.

They may not:

- Modify production risk rules
- Deploy themselves
- Activate live trading
- Change credentials
- Bypass validation

Promotion to production must be explicit.

## 22. Backtesting

Backtests must document:

- Dataset
- Date range
- Market
- Strategy version
- Parameters
- Costs
- Slippage assumptions
- Position sizing
- Risk rules
- Results
- Drawdown
- Limitations

Backtests must avoid look-ahead bias, data leakage, and unrealistic execution assumptions.

A profitable backtest does not authorize live trading.

## 23. Learning Without Uncontrolled Self-Modification

TradeOS should learn from trades, missed opportunities, rejected setups, prediction accuracy, execution quality, market regimes, and strategy performance.

The Learning Agent may recommend changes.

Safety-critical changes require explicit approval and validation.

One outcome is not sufficient evidence for a permanent learning rule.

## 24. Explainability

For every meaningful trade proposal, TradeOS should be able to explain:

1. What setup was detected?
2. Why was it valid?
3. What evidence supported it?
4. What evidence contradicted it?
5. What did the prediction model estimate?
6. What reward was expected?
7. What risk was accepted?
8. Why was the position size selected?
9. Why was the trade approved or rejected?
10. What happened afterward?
11. What was learned?

## 25. Auditability

Important decisions must record:

- Timestamp
- Market
- Instrument
- Agent and version
- Strategy and version
- Input references
- Decision
- Confidence
- Risk assessment
- Risk Engine version/configuration where applicable
- Position size
- Execution result
- Errors
- Outcome

A completed trade should be reconstructable from its records.

## 26. Human Override and Kill Switch

The user must be able to:

- Disable trading
- Change operating mode
- Stop new orders
- Trigger an emergency halt
- Review proposed trades
- Approve/reject trades in Assisted Live mode

The system must provide an emergency mechanism that prevents new trading after severe drawdown, broker failure, data failure, unexpected order behavior, system malfunction, abnormal volatility, security events, or other configured triggers.

## 27. Configuration

Risk and operating parameters must be configuration-driven, including:

```text
risk_per_trade
maximum_daily_loss
maximum_drawdown
maximum_portfolio_exposure
maximum_position_size
maximum_leverage
minimum_liquidity
operating_mode
maximum_agent_iterations
agent_timeout
```

Configuration changes must be logged. Safety-critical limits should be protected against accidental weakening.

## 28. Strategy Independence

Every strategy must have:

- Unique identifier
- Version
- Compatible markets
- Timeframe
- Required data
- Entry rules
- Exit rules
- Risk assumptions
- Position-sizing method
- Validation history
- Performance metrics

Strategies must be independently testable.

## 29. Indicator Governance

Indicators such as EMA, RSI, Fibonacci, MACD, ATR, VWAP, Bollinger Bands, and volume indicators are not automatically predictive.

Their usefulness must be validated within a defined strategy and market context.

Avoid redundant indicators and overfitting.

## 30. Prediction Governance

Prediction models must report uncertainty appropriately.

Track separately:

- Prediction quality
- Strategy quality
- Execution quality
- Risk-management quality

A correct prediction does not guarantee a profitable trade.

## 31. No Hidden Behavior

No component may silently:

- Change strategy parameters
- Change risk parameters
- Increase leverage
- Change operating mode
- Activate live trading
- Modify historical results
- Delete decision records
- Suppress errors

Important state changes must be observable and logged.

## 32. Safe Failure

When a component fails:

```text
Uncertainty
   ↓
Pause / Reject
   ↓
Log
   ↓
Alert
   ↓
Recover or Require Review
```

System uncertainty must never be converted into a trading decision.

## 33. Kill Switches

TradeOS must support authoritative kill switches at appropriate scopes.

Possible scopes include:

- Order
- Instrument
- Strategy
- Account
- Market
- Platform

A kill switch must be enforceable without relying on an LLM's interpretation.

Emergency mode must preserve evidence and support reconciliation rather than destroying state.

## 34. Version Control

Version all important:

- Rules
- Strategies
- Agents
- Models
- Configuration
- Data schemas
- APIs
- Backtests
- Research results
- Architecture decisions

Live decisions must be traceable to the versions that produced them.

## 35. Security

Never commit secrets to GitHub.

This includes broker keys, API secrets, AWS credentials, database passwords, LLM keys, and encryption keys.

Development, paper, and live credentials should be separated where possible.

## 36. Professional Completion Standard

A feature is not complete merely because it works once.

Production candidates must be:

- Documented
- Tested
- Observable
- Reproducible
- Versioned
- Failure-aware
- Reviewable

## 37. Architectural Conflict Rule

When a detailed subsystem design conflicts with these global rules:

1. Stop implementation of the conflicting behavior.
2. Identify the conflict explicitly.
3. Resolve the architecture.
4. Update the affected documentation.
5. Update this document if the global rule itself changes.
6. Only then implement or resume the affected behavior.

Detailed documents may refine these rules but may not silently weaken them.

## 38. Ultimate Rule

When any component is uncertain whether an action is safe:

> **STOP, DO NOT TRADE, AND REQUEST REVIEW.**

## Rule Priority

When rules conflict, use this order:

```text
1. Capital & Safety
2. Risk Controls
3. Data Integrity
4. Portfolio Constraints
5. Execution Safety
6. Validated Strategy
7. Prediction / Analysis
8. Optimization
9. Profit Opportunity
```

**Profit is never allowed to outrank safety.**

---

> **Research deeply. Decide systematically. Risk conservatively. Execute precisely. Learn continuously.**
