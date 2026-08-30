# TradeOS Risk Management

**Document:** 08_RISK_MANAGEMENT.md  
**Version:** 0.1.0  
**Status:** Architecture Baseline  
**Scope:** Risk philosophy, controls, position sizing, portfolio limits, drawdown protection, kill switches, approvals, and risk governance

---

## 1. Purpose

Risk management is the primary safety system of TradeOS.

The purpose of this document is to define how TradeOS prevents a potentially intelligent trading decision from becoming an unacceptable financial risk.

The core principle is:

> **A potentially profitable trade is never sufficient justification for unacceptable risk.**

TradeOS must protect capital before optimizing returns.

---

# 2. Risk Philosophy

TradeOS follows these principles:

1. Preserve capital.
2. Define risk before entry.
3. Never confuse confidence with safety.
4. Never allow an AI agent to bypass hard risk limits.
5. Treat portfolio risk as more important than individual trade attractiveness.
6. Reduce risk as the system becomes uncertain.
7. Stop trading when safety assumptions are no longer valid.
8. Learn from risk violations and repeated mistakes.
9. Make every material risk decision auditable.
10. Prefer no trade over uncontrolled risk.

---

# 3. Risk Hierarchy

Risk controls operate in layers.

```text
Global Safety Rules
        ↓
Account-Level Limits
        ↓
Portfolio Limits
        ↓
Strategy Limits
        ↓
Trade-Level Limits
        ↓
Execution Controls
```

A lower layer cannot override a higher-level restriction.

---

# 4. Risk Components

TradeOS should maintain separate risk components for:

```text
Trade Risk
Position Risk
Portfolio Risk
Market Risk
Liquidity Risk
Leverage Risk
Margin Risk
Execution Risk
Operational Risk
Model Risk
Agent Risk
Data Risk
Behavioral Risk
```

---

# 5. Deterministic Risk Engine

The Deterministic Risk Engine is the primary hard-control mechanism.

It must use deterministic calculations for safety-critical checks.

Examples:

- Position size
- Maximum risk
- Daily loss
- Drawdown
- Exposure
- Leverage
- Margin
- Concentration

An LLM must not be the sole authority for these calculations.

---

# 6. Risk Gate

Every trade intended for execution must pass the Risk Gate.

```text
Trade Proposal
      ↓
Deterministic Risk Engine
      ↓
Risk Agent
      ↓
Risk Gate
      ↓
APPROVE / REJECT / REVIEW
```

Hard constraint failure results in:

```text
REJECT
```

No downstream component may convert a hard rejection into an approval.

---

# 7. Pre-Trade Risk

Before authorization, TradeOS should evaluate:

- Account equity
- Available capital
- Risk per trade
- Stop-loss
- Position size
- Portfolio exposure
- Correlation
- Daily loss
- Drawdown
- Leverage
- Margin
- Liquidity
- Slippage
- Data freshness
- Market status
- Operating mode

---

# 8. Risk Must Be Defined Before Entry

A trade proposal should define risk before execution.

At minimum:

```text
Entry
Stop / Invalidation
Position Size
Maximum Loss
Target / Exit Framework
```

If risk cannot be reasonably defined, the trade should normally be rejected or escalated.

---

# 9. Position Sizing

Position sizing should be derived from predefined risk.

Conceptually:

```text
Maximum Risk Amount
        ÷
Risk Per Unit
        =
Maximum Position Size
```

For a simple long equity example:

```text
Risk Per Unit = Entry Price - Stop Price
```

Then:

```text
Position Size = Maximum Risk Amount / Risk Per Unit
```

Actual implementation must account for:

- Tick size
- Lot size
- Contract multiplier
- Fees
- Slippage
- Currency conversion
- Market-specific rules

---

# 10. Risk Per Trade

Risk per trade should be expressed as a percentage of relevant account equity.

Example:

```text
Account Equity = 100,000
Risk Limit = 0.50%

Maximum Risk = 500
```

This is an illustrative example only.

Actual default thresholds should be configurable and validated.

---

# 11. Maximum Loss

The system should calculate expected maximum loss under the defined stop/invalidation model.

Potential components:

```text
Price Risk
+
Fees
+
Estimated Slippage
+
Currency Effects
```

A trade should not be approved if the resulting risk exceeds the applicable limit.

---

# 12. Risk/Reward

Risk/reward should be calculated using defined assumptions.

Example:

```text
Entry = 100
Stop = 95
Target = 110

Risk = 5
Potential Reward = 10

Reward/Risk = 2.0
```

Risk/reward is one factor, not an automatic approval criterion.

A high reward/risk trade can still be unsafe.

---

# 13. Stop-Loss Governance

A stop must be meaningful to the strategy.

TradeOS should prevent:

- Missing stop where a stop is required
- Arbitrary stop placement
- Stop widening solely to avoid a loss
- Risk increases without authorization

If a strategy supports dynamic stops, the rules must be explicitly defined.

---

# 14. Trailing Stops

Trailing stops may be used only when supported by the strategy.

The system must record:

- Original stop
- Stop adjustments
- Reason
- Strategy rule
- Timestamp
- Risk impact

A trailing stop must not become a hidden mechanism for increasing unacceptable risk.

---

# 15. Daily Loss Limit

TradeOS should maintain an account-level daily loss limit.

Conceptually:

```text
Start-of-Day Equity
       ↓
Realized + Unrealized Loss
       ↓
Daily Loss
       ↓
Compare With Limit
```

If the limit is reached:

```text
STOP NEW TRADING
```

Further behavior should be determined by the configured safety policy.

---

# 16. Drawdown Protection

Drawdown should be monitored at multiple horizons.

Potential measures:

```text
Intraday Drawdown
Daily Drawdown
Weekly Drawdown
Monthly Drawdown
Peak-to-Trough Drawdown
Strategy Drawdown
Portfolio Drawdown
```

Different thresholds may trigger different responses.

---

# 17. Drawdown Response Levels

A configurable framework may include:

```text
NORMAL
      ↓
CAUTION
      ↓
REDUCED_RISK
      ↓
HALT_NEW_TRADES
      ↓
EMERGENCY
```

Exact thresholds must be established through validation and configuration.

---

# 18. Portfolio Exposure

TradeOS should calculate exposure across:

- Individual instruments
- Sectors
- Asset classes
- Markets
- Currencies
- Strategies
- Directions

A portfolio can be unsafe even when every individual trade appears acceptable.

---

# 19. Concentration Risk

TradeOS should identify excessive concentration.

Example:

```text
Trade A → Technology
Trade B → Technology
Trade C → Technology
Trade D → Technology
```

Individual risk may be acceptable while aggregate exposure is not.

The Portfolio/Risk layers must account for this.

---

# 20. Correlation Risk

Highly correlated positions should not be treated as independent.

The system should consider:

- Historical correlation
- Current regime
- Common factors
- Sector relationships
- Market beta

Correlation models must include appropriate uncertainty.

---

# 21. Leverage Risk

TradeOS should track:

```text
Gross Exposure
Net Exposure
Account Equity
Leverage
Margin Used
Available Margin
```

Hard leverage limits must be deterministic.

---

# 22. Margin Risk

For leveraged instruments, TradeOS should monitor:

- Initial margin
- Maintenance margin
- Available margin
- Margin utilization
- Margin stress

The system should act before forced liquidation becomes likely.

---

# 23. Liquidity Risk

Before execution, consider:

- Average volume
- Bid/ask spread
- Market depth
- Expected slippage
- Position size relative to liquidity
- Market session
- Trading halt status

Illiquid trades may require stricter limits.

---

# 24. Slippage Risk

TradeOS should model expected slippage.

Execution assumptions should distinguish:

```text
Intended Price
Actual Fill Price
Expected Slippage
Actual Slippage
```

Actual execution data should feed future analysis.

---

# 25. Gap Risk

For assets capable of large price gaps:

```text
Stop Price
     ≠
Guaranteed Exit Price
```

TradeOS should recognize that a stop order may not eliminate gap risk.

Risk models should account for this where appropriate.

---

# 26. Event Risk

Risk may increase around:

- Earnings
- Economic releases
- Central bank decisions
- Elections
- Major geopolitical events
- Corporate actions
- Contract expiry
- Market-specific events

The News/Event layer should provide information to Risk.

Risk retains authority.

---

# 27. Market Regime Risk

The same strategy can behave differently under different regimes.

Risk should consider:

```text
Strategy
+
Market Regime
+
Historical Performance
```

A strategy may be restricted or require additional confirmation under unfavorable regimes.

---

# 28. Strategy-Level Risk

Each strategy should define:

- Maximum position risk
- Maximum concurrent positions
- Maximum portfolio contribution
- Maximum leverage
- Market eligibility
- Timeframe
- Stop requirements
- Liquidity requirements

Strategy limits cannot exceed global risk limits.

---

# 29. Account-Level Risk

Account-level controls may include:

- Maximum daily loss
- Maximum drawdown
- Maximum leverage
- Maximum margin usage
- Maximum gross exposure
- Maximum net exposure
- Maximum number of open positions

These are higher-level constraints.

---

# 30. Risk Budget

TradeOS should support risk budgeting.

Conceptually:

```text
Total Risk Budget
      ↓
Portfolio Allocation
      ↓
Strategy Allocation
      ↓
Trade Allocation
```

Risk allocation should be explicit.

---

# 31. Portfolio Heat

Portfolio heat represents aggregate open risk.

Conceptually:

```text
Portfolio Heat =
Sum of Defined Risk Across Open Positions
```

Additional methodology may include correlations and stress scenarios.

---

# 32. Stress Testing

TradeOS should support portfolio stress scenarios.

Examples:

```text
Market -2%
Market -5%
Volatility Spike
Sector Shock
Currency Shock
Gap Down
Liquidity Reduction
Correlation Increase
```

Stress results should be informational or restrictive depending on configuration.

---

# 33. Tail Risk

TradeOS should recognize that historical distributions may underestimate extreme events.

Potential controls:

- Exposure caps
- Gap-risk adjustments
- Volatility scaling
- Stress tests
- Concentration limits
- Emergency halts

Tail-risk controls should not rely exclusively on historical averages.

---

# 34. Volatility Scaling

Strategies may optionally adjust exposure based on volatility.

Conceptually:

```text
Higher Volatility
      ↓
Smaller Position

Lower Volatility
      ↓
Potentially Larger Position
```

Any scaling must remain within hard account and strategy limits.

---

# 35. Risk of Ruin

TradeOS should evaluate whether a strategy/account configuration can produce unacceptable capital loss under plausible adverse sequences.

This should be studied during strategy validation.

No strategy should be approved solely because its average return is attractive.

---

# 36. Risk of Repeated Mistakes

Behavioral patterns can create risk.

Examples:

- Repeated overtrading
- Repeated revenge trading
- Repeated stop widening
- Repeated excessive sizing
- Repeated trading after daily loss limits
- Repeated ignoring of warnings

TradeOS should convert validated behavioral patterns into appropriate warnings or restrictions.

---

# 37. Agent Risk

AI agents introduce additional risk.

Potential agent failures:

- Hallucinated information
- Overconfidence
- Incorrect calculations
- Context contamination
- Prompt injection
- Repeated false positives
- Failure to abstain
- Inconsistent recommendations

Agents must therefore remain subordinate to deterministic controls.

---

# 38. Model Risk

Models can:

- Drift
- Become miscalibrated
- Overfit
- Fail under regime changes
- Produce unstable outputs

TradeOS should track:

```text
Model Version
Calibration
Performance
Regime
Sample Size
Drift
```

A degraded model may be disabled or require review.

---

# 39. Data Risk

Incorrect data can create incorrect decisions.

Controls include:

- Freshness checks
- Cross-source validation where practical
- Anomaly detection
- Missing-data handling
- Provider health monitoring

If critical data cannot be trusted:

```text
NO NEW TRADE
```

---

# 40. Operational Risk

Operational failures include:

- Database failure
- Network failure
- Broker failure
- Service outage
- Clock synchronization issues
- Credential failure
- Software defects

Risk controls must account for operational uncertainty.

---

# 41. Execution Risk

Execution risk includes:

- Slippage
- Partial fills
- Rejections
- Latency
- Duplicate orders
- Unknown order status
- Broker disconnect

The execution system must reconcile state before proceeding when necessary.

---

# 42. Pre-Trade Checklist

A trade should pass checks such as:

```text
[ ] Instrument valid
[ ] Market open / eligible
[ ] Data fresh
[ ] Strategy valid
[ ] Entry defined
[ ] Stop defined
[ ] Position size calculated
[ ] Maximum loss within limit
[ ] Portfolio exposure acceptable
[ ] Leverage acceptable
[ ] Margin acceptable
[ ] Liquidity acceptable
[ ] Event risk reviewed
[ ] Operating mode permits action
[ ] Risk approved
```

---

# 43. Risk Decision Codes

Risk decisions should use structured reason codes.

Examples:

```text
RISK_OK
RISK_PER_TRADE_EXCEEDED
DAILY_LOSS_LIMIT
DRAWDOWN_LIMIT
PORTFOLIO_EXPOSURE
CONCENTRATION
LEVERAGE
MARGIN
LIQUIDITY
STALE_DATA
MARKET_CLOSED
STRATEGY_NOT_APPROVED
UNKNOWN_POSITION_STATE
SYSTEM_SAFETY
```

This enables analytics and learning.

---

# 44. Risk Decision Record

Every material risk decision should preserve:

```text
timestamp
trade_proposal_id
account
equity
risk_amount
risk_percent
position_size
portfolio_state
drawdown
daily_loss
leverage
margin
decision
reason_codes
risk_engine_version
risk_configuration_version
risk_agent_version
```

---

# 45. Risk Overrides

Overrides should be extremely limited.

Any permitted override must be:

- Explicit
- Authorized
- Logged
- Attributed
- Time-limited where possible
- Re-evaluated by Risk

An override must never disable immutable safety constraints.

---

# 46. Kill Switches

TradeOS should support multiple kill switches.

```text
USER KILL SWITCH
       ↓
RISK KILL SWITCH
       ↓
SYSTEM SAFETY KILL SWITCH
       ↓
BROKER / EXECUTION SAFETY
```

Any authoritative safety mechanism may stop new trading.

---

# 47. Kill Switch Scope

A kill switch may apply to:

- One order
- One instrument
- One strategy
- One account
- One market
- Entire platform

Scope must be explicit.

---

# 48. Emergency State

Emergency mode should:

- Block new trading
- Preserve auditability
- Reconcile open orders
- Reconcile positions
- Notify authorized users
- Preserve system evidence

Emergency mode should not destroy data.

---

# 49. Risk Recovery

After a halt:

```text
HALT
 ↓
DIAGNOSE
 ↓
RECONCILE
 ↓
VALIDATE
 ↓
APPROVE RESUMPTION
 ↓
RESUME
```

Restarting a service is not equivalent to validating safety.

---

# 50. Risk Monitoring

Risk should be monitored continuously or at appropriate event intervals.

Monitor:

- Equity
- P&L
- Drawdown
- Exposure
- Margin
- Leverage
- Position count
- Liquidity
- Data health
- Broker health
- Agent health

---

# 51. Risk Alerts

Alerts should be prioritized.

Example severity:

```text
INFO
WARNING
HIGH
CRITICAL
EMERGENCY
```

Critical risk events should require immediate attention according to deployment policy.

---

# 52. Risk Reporting

TradeOS should produce:

### Real-Time

- Current risk
- Exposure
- Drawdown
- Margin
- Open positions

### Daily

- Risk usage
- Violations
- Largest risks
- P&L
- Trade quality

### Weekly

- Risk trends
- Strategy risk
- Behavioral risk
- Agent risk

### Monthly

- Drawdown
- Tail-risk observations
- Risk-adjusted performance
- System reliability

---

# 53. Risk Learning Loop

Risk outcomes should feed the Learning System.

```text
Risk Decision
      ↓
Trade Outcome
      ↓
Compare Expected vs Actual
      ↓
Risk Pattern
      ↓
Learning Candidate
      ↓
Validation
      ↓
Approved Improvement
```

Examples:

- Slippage consistently underestimated
- Certain market regimes produce excessive loss
- Position sizing too aggressive
- Specific strategy creates concentration risk

---

# 54. Risk Mistake Detection

The system should identify:

```text
Expected Risk
      vs
Actual Risk
```

Potential mistakes:

- Risk calculation error
- Incorrect position size
- Stop mismatch
- Unexpected leverage
- Unexpected slippage
- Portfolio exposure underestimated

System-level risk mistakes must be treated differently from ordinary trade losses.

---

# 55. Risk and Learning Boundaries

Learning may recommend:

- More conservative sizing
- Additional validation
- Strategy restrictions
- Regime restrictions
- Better slippage assumptions

Learning may not independently:

- Increase risk limits
- Disable daily loss limits
- Disable drawdown protection
- Disable kill switches
- Override deterministic rejection

---

# 56. Risk and Agent Hierarchy

The authority relationship is:

```text
Agent Analysis
      ↓
Strategy
      ↓
Critic
      ↓
Portfolio
      ↓
Deterministic Risk Engine
      ↓
Risk Gate
      ↓
Execution
```

Risk is a gate, not another opinion.

---

# 57. No-Trade Principle

TradeOS should actively prefer:

```text
NO TRADE
```

when:

- Evidence is weak
- Risk is unclear
- Data is stale
- Portfolio exposure is excessive
- Market conditions are unsuitable
- System state is uncertain
- Strategy conditions are incomplete

A system that trades constantly is not necessarily a good trading system.

---

# 58. Risk Testing

Risk controls require deterministic tests.

Minimum categories:

### Unit Tests

- Position sizing
- Risk percentage
- Drawdown
- Leverage
- Margin

### Boundary Tests

- Exactly at limit
- Just below limit
- Just above limit

### Failure Tests

- Missing data
- Missing stop
- Unknown position
- Broker unavailable
- Risk engine unavailable

### Scenario Tests

- Gap
- Volatility spike
- Multiple correlated losses
- Daily loss threshold
- Drawdown threshold

---

# 59. Risk Simulation

Before live deployment, simulate:

```text
Normal Market
Volatile Market
Gap Market
Illiquid Market
Broker Failure
Data Failure
Agent Failure
Portfolio Shock
```

The expected safety behavior must be documented.

---

# 60. Risk Configuration

Risk parameters should be configuration-driven but protected.

Examples:

```text
max_risk_per_trade
max_daily_loss
max_drawdown
max_leverage
max_margin_utilization
max_portfolio_heat
max_position_count
max_concentration
```

Exact defaults should be determined through validated configuration.

---

# 61. Configuration Hierarchy

Risk configuration should follow:

```text
Global Maximum
      ↓
Account Maximum
      ↓
Strategy Maximum
      ↓
Trade Requested Risk
```

The effective risk must never exceed the smallest applicable hard limit.

---

# 62. Risk Versioning

Historical risk decisions must reference:

```text
risk_engine_version
risk_configuration_version
```

This allows later reconstruction of why a trade was approved or rejected.

---

# 63. Risk Architecture Invariants

The following are non-negotiable:

1. Risk is authoritative.
2. Hard risk controls are deterministic.
3. Execution cannot bypass Risk.
4. Missing critical risk information blocks execution.
5. Unknown broker state requires reconciliation.
6. Daily loss protection cannot be silently disabled.
7. Drawdown protection cannot be silently disabled.
8. Kill switches are authoritative.
9. Learning cannot increase risk without explicit governance.
10. Every material risk decision is auditable.
11. Confidence never overrides risk.
12. No trade is preferable to unsafe trade.

---

# 64. Initial Risk Implementation

The first implementation should focus on:

```text
Account Equity
      ↓
Risk Per Trade
      ↓
Position Sizing
      ↓
Stop Validation
      ↓
Daily Loss
      ↓
Drawdown
      ↓
Portfolio Exposure
      ↓
Risk Gate
      ↓
Paper Execution
```

Then add:

```text
Correlation
Leverage
Margin
Liquidity
Stress Testing
Behavioral Risk
Agent Risk
Advanced Tail Risk
```

---

# 65. Risk Architecture Success Criteria

The risk architecture is successful when:

- Unsafe trades are deterministically rejected.
- Position size is reproducible.
- Daily loss protection works.
- Drawdown protection works.
- Portfolio exposure is visible.
- Unknown execution states are contained.
- Kill switches work independently of AI reasoning.
- Risk decisions are auditable.
- Learning can identify recurring risk problems.
- Risk controls cannot be weakened by an agent.

---

# 66. Related Documents

- `README.md`
- `rules.md`
- `docs/01_PROJECT_VISION.md`
- `docs/02_DESIGN_PRINCIPLES.md`
- `docs/03_ENGINEERING_PRINCIPLES.md`
- `docs/04_SYSTEM_ARCHITECTURE.md`
- `docs/05_AGENT_ARCHITECTURE.md`
- `docs/06_DATA_ARCHITECTURE.md`
- `docs/07_TRADING_WORKFLOWS.md`
- `docs/09_PREDICTION_ENGINE.md`
- `docs/10_LEARNING_SYSTEM.md`
- `docs/11_BACKTESTING_AND_VALIDATION.md`
- `docs/12_EXECUTION_ARCHITECTURE.md`
- `docs/20_AGENT_CONTRACTS.md`
- `docs/21_CONFIGURATION.md`

---

## Version History

| Version | Status | Description |
|---|---|---|
| 0.1.0 | Architecture Baseline | Initial TradeOS risk architecture, including deterministic risk controls, portfolio protection, kill switches, and risk learning |

---

> **Risk principle: intelligence may identify opportunity, but only governed risk can permit exposure.**
