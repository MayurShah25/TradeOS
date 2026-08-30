# TradeOS Global Rules

**Version:** 0.2.0  
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

## 3. Risk Before Entry

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

## 4. Position Sizing

The initial personal-testing baseline is approximately **0.5% of account equity risk per trade**, subject to final validation and configuration.

Conceptually:

```text
Risk Amount = Account Equity × Allowed Risk %

Risk Per Unit = |Entry Price - Stop Price|

Position Size = Risk Amount / Risk Per Unit
```

Final quantity must also respect lot sizes, contract specifications, available capital, leverage, liquidity, broker rules, and portfolio exposure.

Never increase position size to recover losses.

## 5. Drawdown and Daily Loss Protection

TradeOS must support configurable drawdown states that progressively reduce risk and ultimately halt new trading.

Example:

```text
NORMAL → CAUTION → REDUCED_RISK → TRADING_HALT
```

The system must also maintain a daily loss budget. Once the configured limit is reached, no new discretionary trades may be opened.

Existing positions may continue to be managed according to their approved exit and safety rules.

## 6. Stop-Loss Rules

1. Every trade must have an invalidation mechanism.
2. A stop-loss must be established before or immediately with entry.
3. A stop may be tightened.
4. A stop must never be widened simply to avoid realizing a loss.
5. Increased model confidence cannot remove risk controls.
6. If the trade thesis is invalidated, the approved exit rules take precedence.

## 7. Let Winners Run

When a trade moves strongly in the expected direction and the thesis remains valid, the system should avoid prematurely closing it solely to secure a small profit.

Permitted mechanisms include:

- Trailing stop-loss
- Trailing take-profit
- Dynamic profit protection
- Partial profit-taking
- Trend-based exits
- Volatility-adjusted trailing

Trailing logic must be predefined. Stops may move toward reduced risk but never be widened merely to give a losing position more room.

## 8. Portfolio Risk

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

## 9. Multi-Market Architecture

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

## 10. Agent Governance

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

### Risk Agent

Calculates risk, position size, exposure, and trade eligibility.

**Has hard veto authority.**

### Execution Agent

Executes only approved orders and verifies actual broker state.

Cannot create its own trading thesis or bypass Risk.

### Learning Agent

Analyzes outcomes and proposes improvements.

Cannot automatically modify immutable safety controls or deploy unvalidated strategies.

### Coach Agent

Explains decisions and creates learning reports.

Cannot override trading controls.

## 11. Risk Veto

The decision hierarchy is:

```text
Research / Market Analysis
        ↓
Strategy
        ↓
Prediction
        ↓
Critic
        ↓
Portfolio
        ↓
RISK GATE
        ↓
Execution
```

If the Risk Gate returns `REJECT`, execution is prohibited.

## 12. Inter-Agent Communication

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

## 13. Token Efficiency

Agents must not read the entire repository for every decision.

Use only relevant context:

```text
Repository
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

## 14. Data Integrity

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

## 15. Execution Safety

Before and during execution, verify:

- Broker connectivity
- Authentication
- Order status
- Filled quantity
- Average fill price
- Position state
- Available capital/margin

Never assume an order filled without verification.

## 16. Operating Modes

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

## 17. Research / Production Separation

New strategies and models begin in a research sandbox.

They may test hypotheses, indicators, models, and strategies.

They may not:

- Modify production risk rules
- Deploy themselves
- Activate live trading
- Change credentials
- Bypass validation

Promotion to production must be explicit.

## 18. Backtesting

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

A profitable backtest does not authorize live trading.

## 19. Learning Without Uncontrolled Self-Modification

TradeOS should learn from trades, missed opportunities, rejected setups, prediction accuracy, execution quality, market regimes, and strategy performance.

The Learning Agent may recommend changes.

Safety-critical changes require explicit approval and validation.

## 20. Explainability

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

## 21. Auditability

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
- Position size
- Execution result
- Errors
- Outcome

A completed trade should be reconstructable from its records.

## 22. Human Override and Kill Switch

The user must be able to:

- Disable trading
- Change operating mode
- Stop new orders
- Trigger an emergency halt
- Review proposed trades
- Approve/reject trades in Assisted Live mode

The system must provide an emergency mechanism that prevents new trading after severe drawdown, broker failure, data failure, unexpected order behavior, system malfunction, abnormal volatility, security events, or other configured triggers.

## 23. Configuration

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

## 24. Strategy Independence

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

## 25. Indicator Governance

Indicators such as EMA, RSI, Fibonacci, MACD, ATR, VWAP, Bollinger Bands, and volume indicators are not automatically predictive.

Their usefulness must be validated within a defined strategy and market context.

Avoid redundant indicators and overfitting.

## 26. Prediction Governance

Prediction models must report uncertainty appropriately.

Track separately:

- Prediction quality
- Strategy quality
- Execution quality
- Risk-management quality

A correct prediction does not guarantee a profitable trade.

## 27. No Hidden Behavior

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

## 28. Safe Failure

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

## 29. Version Control

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

## 30. Security

Never commit secrets to GitHub.

This includes broker keys, API secrets, AWS credentials, database passwords, LLM keys, and encryption keys.

Development, paper, and live credentials should be separated where possible.

## 31. Professional Completion Standard

A feature is not complete merely because it works once.

Production candidates must be:

- Documented
- Tested
- Observable
- Reproducible
- Versioned
- Failure-aware
- Reviewable

## 32. Ultimate Rule

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
