# TradeOS Portfolio Architecture

**Document:** 13_PORTFOLIO_ARCHITECTURE.md  
**Version:** 0.1.0  
**Status:** Architecture Baseline  
**Scope:** Portfolio state, positions, exposure, allocation, concentration, correlation, portfolio risk, portfolio decisions, reconciliation, and portfolio learning

---

## 1. Purpose

The Portfolio Architecture defines how TradeOS understands and manages the state of the overall portfolio.

The core principle is:

> **A trade must be evaluated as part of a portfolio, not in isolation.**

A collection of individually acceptable trades can create an unacceptable aggregate risk.

---

# 2. Portfolio Philosophy

TradeOS should continuously distinguish:

```text
Trade Risk
    ↓
Position Risk
    ↓
Portfolio Risk
```

Portfolio decisions should consider:

- Existing positions
- Pending orders
- Available capital
- Exposure
- Correlation
- Concentration
- Leverage
- Margin
- Strategy allocation
- Market regime

---

# 3. Portfolio Architecture

```text
Market Data
     +
Orders
     +
Fills
     +
Positions
     +
Account State
     +
Risk State
     ↓
Portfolio State Engine
     ↓
Exposure / Correlation / Concentration
     ↓
Portfolio Analysis
     ↓
Risk Gate
```

---

# 4. Portfolio as a State

The Portfolio State should represent the current known portfolio.

It may include:

```text
account
cash
buying_power
equity
positions
open_orders
exposure
margin
leverage
drawdown
portfolio_heat
```

The state should be timestamped.

---

# 5. Position

A position represents actual held exposure.

Potential fields:

```text
position_id
account_id
instrument_id
quantity
average_entry_price
market_price
market_value
unrealized_pnl
realized_pnl
currency
opened_at
updated_at
```

Actual position state should ultimately reconcile with the broker.

---

# 6. Position vs Trade

Trade and position are not necessarily the same entity.

Example:

```text
Trade A
  ↓
Position Open
  ↓
Partial Exit
  ↓
Trade B / Additional Entry
  ↓
Position Continues
```

The data model should preserve the distinction.

---

# 7. Portfolio Snapshot

TradeOS should periodically create portfolio snapshots.

A snapshot may include:

```text
timestamp
equity
cash
buying_power
gross_exposure
net_exposure
margin_used
leverage
position_count
portfolio_heat
drawdown
```

Snapshots support historical analysis.

---

# 8. Account State

Account state may include:

- Cash
- Equity
- Buying power
- Margin
- Available margin
- Realized P&L
- Unrealized P&L

Broker-provided values should be treated as external state and reconciled.

---

# 9. Portfolio Exposure

Exposure should be calculated across multiple dimensions.

```text
Instrument
Sector
Asset Class
Currency
Market
Strategy
Direction
```

---

# 10. Gross Exposure

Gross exposure represents aggregate absolute exposure.

Conceptually:

```text
Gross Exposure
=
Sum of Absolute Position Values
```

Exact treatment depends on asset class.

---

# 11. Net Exposure

Net exposure represents directional exposure after considering long/short positions where meaningful.

Conceptually:

```text
Long Exposure
-
Short Exposure
```

Asset-specific methodology should be used.

---

# 12. Directional Exposure

Track:

```text
LONG
SHORT
NEUTRAL
```

at:

- Portfolio level
- Strategy level
- Market level
- Sector level

---

# 13. Concentration

Portfolio concentration should be evaluated by:

```text
Instrument
Sector
Market
Asset Class
Strategy
Factor
Currency
```

A portfolio can be diversified by instrument but concentrated by factor.

---

# 14. Correlation

TradeOS should estimate relationships among positions where appropriate.

Potential inputs:

- Historical returns
- Current volatility
- Market regime
- Factor exposure

Correlation should be treated as uncertain and time-varying.

---

# 15. Correlation Clusters

The system may group positions into clusters.

Example:

```text
Cluster A
 ├── Technology Stock 1
 ├── Technology Stock 2
 └── Technology ETF

Cluster B
 ├── Energy Stock 1
 └── Energy ETF
```

This can reveal hidden concentration.

---

# 16. Portfolio Heat

Portfolio heat represents aggregate defined risk.

Conceptually:

```text
Portfolio Heat
=
Aggregate Risk of Open Positions
```

Methodology may later incorporate correlations and stress scenarios.

---

# 17. Portfolio Risk Budget

A portfolio may have a total risk budget.

```text
Total Portfolio Risk Budget
        ↓
Strategy Budgets
        ↓
Trade Budgets
```

Allocations must remain below higher-level limits.

---

# 18. Strategy Allocation

Track exposure and risk by strategy.

Example:

```text
Breakout
  Exposure: X
  Risk: Y

Mean Reversion
  Exposure: A
  Risk: B
```

This enables strategy-level portfolio management.

---

# 19. Market Allocation

Track exposure by market.

Example:

```text
US Equities
Futures
FX
Crypto
Fixed Income
```

Exact asset classes depend on TradeOS scope.

---

# 20. Sector Allocation

For assets with sector classifications, track:

```text
Sector
Exposure
Risk
Position Count
```

Sector data should have a source and timestamp.

---

# 21. Currency Exposure

For multi-currency portfolios, track:

```text
Base Currency
Position Currency
Currency Exposure
Hedging Exposure
```

Currency conversion rates must be timestamped.

---

# 22. Factor Exposure

Future versions may track:

- Market beta
- Momentum
- Value
- Size
- Volatility
- Rates
- Commodity sensitivity

Factor models must be versioned.

---

# 23. Portfolio Scenarios

TradeOS should support scenario analysis.

Examples:

```text
Market -2%
Market -5%
Sector Shock
Volatility Spike
Currency Shock
Rate Shock
Correlation Increase
Liquidity Reduction
```

---

# 24. Stress Testing

Stress testing should estimate potential portfolio impact under defined scenarios.

Results should be clearly labeled as simulations.

---

# 25. Portfolio Optimization

Optimization should be introduced only after portfolio state and risk controls are reliable.

Potential objectives:

- Risk-adjusted return
- Volatility reduction
- Diversification
- Exposure control

Optimization must remain subordinate to hard Risk limits.

---

# 26. Portfolio Decision

The Portfolio Agent may return:

```text
APPROVE
REDUCE
REVIEW
REJECT
```

This is portfolio guidance.

The deterministic Risk Engine remains authoritative for hard constraints.

---

# 27. New Trade Impact

For every proposed trade, calculate:

```text
Current Portfolio
      +
Proposed Position
      ↓
Projected Portfolio
```

Then compare:

```text
Exposure
Heat
Concentration
Leverage
Margin
Drawdown
```

---

# 28. Pre-Trade Portfolio Check

Before execution:

```text
Current State
      ↓
Proposed Trade
      ↓
Projected State
      ↓
Portfolio Limits
      ↓
Risk Gate
```

---

# 29. Portfolio Conflict

A trade can be individually attractive but portfolio-inappropriate.

Example:

```text
Trade:
Strong Setup

Portfolio:
Already heavily exposed to same factor
```

Possible result:

```text
REDUCE SIZE
REVIEW
NO TRADE
```

according to configuration.

---

# 30. Position Addition

When adding to an existing position, evaluate:

```text
Current Position
      +
New Quantity
      ↓
New Average Exposure
      ↓
New Risk
```

Adding to a position is not automatically equivalent to a new independent trade.

---

# 31. Scaling In

Strategies that support scaling in must explicitly define:

- Maximum entries
- Maximum total size
- Risk aggregation
- Stop methodology
- Average price handling

---

# 32. Scaling Out

Partial exits should update:

- Quantity
- Average cost methodology
- Realized P&L
- Remaining risk
- Remaining target

---

# 33. Portfolio Cash Management

Track:

```text
Cash
Reserved Cash
Buying Power
Margin
Pending Order Commitments
```

The system should avoid double-counting available capital.

---

# 34. Pending Orders

Portfolio state should account for open orders that may create future exposure.

Example:

```text
Current Exposure
+
Potential Exposure
```

Risk policy should define whether pending orders consume risk budget.

---

# 35. Portfolio Liquidity

Evaluate whether the portfolio can be exited under plausible market conditions.

Potential metrics:

- Position liquidity
- Aggregate liquidity
- Spread
- Market depth
- Exit time assumptions

---

# 36. Portfolio Drawdown

Track:

```text
Current Equity
Peak Equity
Drawdown
```

Also track:

```text
Daily
Weekly
Monthly
Strategy
Portfolio
```

---

# 37. Portfolio Recovery

After drawdown, TradeOS may operate under reduced risk according to configuration.

Example:

```text
Normal
 ↓
Drawdown
 ↓
Reduced Risk
 ↓
Recovery
 ↓
Normal
```

Recovery rules must be deterministic and governed.

---

# 38. Portfolio Rebalancing

Rebalancing may be:

```text
Scheduled
Threshold-Based
Risk-Based
User-Initiated
```

Rebalancing actions must pass Risk.

---

# 39. Rebalancing Constraints

Potential constraints:

- Minimum trade size
- Maximum turnover
- Transaction costs
- Tax considerations where applicable
- Liquidity
- Risk limits

---

# 40. Portfolio Monitoring

Monitor:

- Equity
- Exposure
- Heat
- Drawdown
- Leverage
- Margin
- Concentration
- Correlation
- Liquidity
- Open orders

---

# 41. Portfolio Events

Potential events:

```text
POSITION_OPENED
POSITION_INCREASED
POSITION_REDUCED
POSITION_CLOSED
EXPOSURE_CHANGED
MARGIN_CHANGED
DRAWDOWN_CHANGED
CONCENTRATION_BREACH
PORTFOLIO_MISMATCH
```

---

# 42. Portfolio Reconciliation

Reconcile:

```text
TradeOS Portfolio
      vs
Broker Account
```

Compare:

- Positions
- Quantities
- Average prices where available
- Open orders
- Cash
- Buying power
- Margin

---

# 43. Portfolio Mismatch

If state differs:

```text
MISMATCH
      ↓
Alert
      ↓
Reconcile
      ↓
Restrict dependent actions if necessary
```

Do not silently overwrite one source with another.

---

# 44. Portfolio Data Authority

A source should be designated for each field.

Example:

```text
Broker
→ Actual Position

TradeOS
→ Strategy Metadata

Risk Engine
→ Risk Decision

Market Data Provider
→ Market Price
```

The system should avoid ambiguous authority.

---

# 45. Portfolio History

Historical snapshots should allow questions such as:

> What did the portfolio look like when this trade was approved?

and:

> What exposure existed immediately before the order?

---

# 46. Portfolio Audit

For each trade, preserve:

```text
Portfolio Before
Trade Proposal
Projected Portfolio
Risk Decision
Execution
Portfolio After
```

---

# 47. Portfolio Learning

Portfolio outcomes should feed the Learning System.

Potential patterns:

- Repeated concentration
- Correlation underestimated
- Excessive strategy overlap
- Poor rebalancing
- Liquidity mismatch

---

# 48. Portfolio Mistakes

Portfolio mistakes should be separated from trade mistakes.

Example:

```text
Individual Trade:
Good

Portfolio Decision:
Poor

Result:
Excessive aggregate exposure
```

This distinction is important for learning.

---

# 49. Portfolio Learning Interventions

Possible interventions:

```text
Exposure Warning
Concentration Warning
Reduce Size
Require Review
Strategy Restriction
```

Risk remains authoritative.

---

# 50. Portfolio Optimization Learning

If optimization is used, TradeOS should evaluate:

```text
Predicted Benefit
vs
Realized Benefit
```

Optimization recommendations should not be assumed to improve the portfolio.

---

# 51. Portfolio Simulation

Before material allocation changes:

```text
Current Portfolio
      ↓
Proposed Allocation
      ↓
Stress Test
      ↓
Risk Evaluation
```

---

# 52. Portfolio and Prediction

Prediction outputs may affect projected scenarios but do not override portfolio constraints.

Example:

```text
Strong Prediction
+
High Existing Exposure
=
Potential No-Trade
```

---

# 53. Portfolio and Strategy

Strategy-specific exposure should be visible.

A strategy must not unintentionally duplicate exposure already created by another strategy.

---

# 54. Portfolio and Execution

Execution must receive current portfolio state where needed.

A stale portfolio snapshot should not be treated as current if material changes have occurred.

---

# 55. Portfolio and Learning

Learning should be able to identify:

```text
Strategy overlap
Repeated concentration
Repeated correlation failure
Repeated liquidity stress
```

---

# 56. Portfolio State Freshness

Portfolio state should include timestamps.

Example:

```text
portfolio_snapshot_timestamp
position_update_timestamp
account_update_timestamp
```

Materially stale state should trigger revalidation.

---

# 57. Portfolio State Consistency

TradeOS should detect inconsistent states such as:

```text
Position Quantity ≠ Sum of Reconciled Fills
```

or:

```text
Portfolio Exposure ≠ Sum of Position Exposures
```

These should trigger investigation.

---

# 58. Portfolio Architecture Invariants

The following must remain true:

1. Portfolio risk is distinct from trade risk.
2. Actual positions are reconciled.
3. Pending orders are considered where relevant.
4. Exposure is calculated consistently.
5. Concentration is monitored.
6. Correlation is treated as dynamic.
7. Portfolio checks occur before execution.
8. Hard Risk limits remain authoritative.
9. Historical portfolio state is preserved.
10. Portfolio mismatches are visible.
11. Portfolio learning is distinct from trade learning.
12. Stale portfolio state cannot silently authorize material exposure.
13. Optimization cannot bypass Risk.
14. No trade is required merely to improve utilization.

---

# 59. Initial Portfolio Implementation

The first implementation should focus on:

```text
Account
 ↓
Positions
 ↓
Open Orders
 ↓
Portfolio Snapshot
 ↓
Gross / Net Exposure
 ↓
Portfolio Heat
 ↓
Pre-Trade Impact
 ↓
Risk Gate
```

Then add:

```text
Correlation
Concentration
Factor Exposure
Stress Testing
Optimization
Advanced Rebalancing
```

---

# 60. Portfolio Architecture Success Criteria

The Portfolio System is successful when TradeOS can:

- Maintain an accurate portfolio state.
- Reconcile with broker state.
- Calculate exposure.
- Track portfolio heat.
- Detect concentration.
- Account for pending orders.
- Project the impact of new trades.
- Support portfolio stress tests.
- Preserve historical portfolio snapshots.
- Learn from recurring portfolio mistakes.
- Prevent portfolio-level risk from being hidden by trade-level analysis.

---

# 61. Related Documents

- `README.md`
- `rules.md`
- `docs/04_SYSTEM_ARCHITECTURE.md`
- `docs/05_AGENT_ARCHITECTURE.md`
- `docs/06_DATA_ARCHITECTURE.md`
- `docs/07_TRADING_WORKFLOWS.md`
- `docs/08_RISK_MANAGEMENT.md`
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
| 0.1.0 | Architecture Baseline | Initial TradeOS portfolio architecture, including state management, exposure, concentration, correlation, portfolio risk, reconciliation, and portfolio learning |

---

> **Portfolio principle: every trade changes the portfolio, and every portfolio change must be evaluated in the context of the risk already being carried.**
