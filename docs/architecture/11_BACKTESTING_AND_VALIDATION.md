# TradeOS Backtesting and Validation

**Document:** 11_BACKTESTING_AND_VALIDATION.md  
**Version:** 0.2.0  
**Status:** Architecture Baseline  
**Scope:** Strategy validation, model validation, agent evaluation, backtesting, walk-forward analysis, robustness, paper trading, promotion, and research governance

---

## 1. Purpose

The Backtesting and Validation System exists to answer one fundamental question:

> **Does this idea demonstrate sufficient evidence to justify moving to the next level of deployment?**

TradeOS must not confuse:

```text
Interesting
    ≠
Promising
    ≠
Validated
    ≠
Production Ready
```

The core principle is:

> **No strategy, model, agent, or learning intervention reaches production without passing its defined validation gates.**

Validation establishes evidence and promotion eligibility; it does not itself authorize live trading. Live authorization remains governed by the production risk and execution architecture.

---

# 2. Validation Philosophy

Validation should favor:

- Out-of-sample evidence
- Realistic assumptions
- Reproducibility
- Robustness
- Statistical discipline
- Regime awareness
- Conservative interpretation
- Independent evaluation

A backtest is evidence, not proof.

---

# 3. Validation Layers

TradeOS should use multiple validation layers:

```text
Code Validation
      ↓
Unit Tests
      ↓
Data Validation
      ↓
Backtest
      ↓
Robustness Tests
      ↓
Out-of-Sample
      ↓
Walk-Forward
      ↓
Paper Trading
      ↓
Controlled Promotion
```

The exact sequence may vary by artifact.

Validation should escalate in depth only as evidence, uncertainty, artifact impact, or promotion risk justifies it. A workflow should not invoke every model, agent, simulation, or test merely because those capabilities are available.

---

# 4. What Must Be Validated

The framework applies to:

```text
Strategies
Prediction Models
Agent Behavior
Risk Rules
Execution Logic
Learning Rules
Feature Sets
Configurations
```

---

# 5. Strategy Lifecycle

A strategy should progress through:

```text
IDEA
 ↓
RESEARCH
 ↓
IMPLEMENTATION
 ↓
BACKTEST
 ↓
ROBUSTNESS
 ↓
OUT-OF-SAMPLE
 ↓
WALK-FORWARD
 ↓
PAPER
 ↓
REVIEW
 ↓
APPROVED
 ↓
PRODUCTION
```

No direct path from IDEA to PRODUCTION.

---

# 6. Backtest Definition

Every backtest must define:

```text
Strategy
Strategy Version
Dataset
Date Range
Timeframe
Universe
Parameters
Starting Capital
Fees
Slippage
Execution Assumptions
Market Hours
Position Rules
Risk Rules
Software Version
```

---

# 7. Reproducibility

A backtest should be reproducible.

Record:

- Dataset version
- Strategy version
- Code version
- Configuration version
- Model version
- Feature version
- Random seed where relevant
- Execution assumptions

A result that cannot be reproduced should receive reduced trust.

---

# 8. Historical Data Integrity

Before backtesting, validate:

- Missing observations
- Duplicates
- Timestamp integrity
- Corporate actions
- Symbol changes
- Delisted instruments where relevant
- Adjustments
- Data provider consistency

Bad data can create fake performance.

---

# 9. Look-Ahead Bias

Look-ahead bias occurs when information unavailable at decision time enters a historical decision.

Examples:

```text
Future price
Future volume
Future corporate event
Future revised fundamental data
Future news classification
```

Backtests must prevent this.

---

# 10. Data Leakage

Data leakage includes any unintended transfer of future information into training or evaluation.

This is especially important for:

- Machine learning
- Prediction models
- LLM-assisted systems
- Feature engineering

Every feature should have a valid historical availability timestamp.

---

# 11. Survivorship Bias

Where applicable, the historical universe should include instruments that later disappeared.

Otherwise a strategy may look artificially strong because failed instruments were removed.

---

# 12. Selection Bias

TradeOS should document how:

- Instruments
- Strategies
- Parameters
- Time periods
- Models

were selected.

Repeatedly selecting only successful experiments creates misleading results.

---

# 13. Multiple Testing

Testing hundreds or thousands of ideas increases the chance of finding apparently successful results by chance.

TradeOS should track:

```text
Experiments Run
Parameters Tested
Strategies Tested
Model Variants
Selection Process
```

---

# 14. Parameter Overfitting

A strategy should not depend on extremely precise parameters without evidence of robustness.

Example:

```text
Parameter = 17
```

performing dramatically better than:

```text
16, 18, 19, 20
```

may indicate overfitting.

---

# 15. Parameter Sensitivity

Test reasonable parameter ranges.

Example:

```text
Fast MA:
18
20
22
24

Slow MA:
45
50
55
60
```

The goal is to identify stable regions rather than a single optimal point.

---

# 16. Robustness Testing

Robustness tests may vary:

- Parameters
- Entry timing
- Exit timing
- Slippage
- Fees
- Data period
- Market
- Regime
- Position sizing
- Execution assumptions

A robust strategy should not collapse under small reasonable changes.

---

# 17. Slippage Testing

Test multiple slippage assumptions.

Example:

```text
0.00%
0.05%
0.10%
0.20%
0.50%
```

The exact levels depend on the market.

If a strategy only works with unrealistically low slippage, it should be rejected or reconsidered.

---

# 18. Transaction Cost Testing

Include:

- Commissions
- Exchange fees
- Bid/ask spread
- Financing costs
- Borrow costs where applicable
- Market impact where material

Gross returns should not be confused with net returns.

---

# 19. Execution Modeling

Backtests should distinguish:

```text
Signal Price
Expected Execution
Actual / Simulated Fill
```

Execution assumptions should be conservative.

---

# 20. Liquidity Constraints

The simulation should consider:

- Volume
- Spread
- Market depth where available
- Position size
- Market impact

A strategy should not assume unlimited liquidity.

---

# 21. Partial Fills

Where relevant, backtests should model partial fills.

This is especially important for:

- Large orders
- Illiquid instruments
- Fast markets

---

# 22. Market Hours

The simulator must understand:

- Market open
- Market close
- Holidays
- Trading halts
- Pre-market
- After-hours
- Session-specific rules

No trade should be simulated at an impossible time.

---

# 23. Corporate Actions

For applicable instruments, consider:

- Splits
- Dividends
- Mergers
- Spinoffs
- Symbol changes

Corporate-action treatment must be documented.

---

# 24. Performance Metrics

Minimum strategy metrics should include:

- Total return
- Net return
- Annualized return where appropriate
- Maximum drawdown
- Win rate
- Average win
- Average loss
- Profit factor
- Expectancy
- Trade count
- Exposure
- Turnover

Additional risk-adjusted metrics may include:

- Sharpe
- Sortino
- Calmar

---

# 25. Metrics Must Have Context

No single metric should determine approval.

For example:

```text
High Return
+
Extreme Drawdown
```

may be unacceptable.

Similarly:

```text
High Win Rate
+
Very Large Average Loss
```

may be dangerous.

---

# 26. Trade-Level Analysis

Backtests should retain trade-level records.

Useful fields:

```text
entry
exit
quantity
P&L
fees
slippage
duration
strategy
regime
reason
```

This enables later learning.

---

# 27. Equity Curve Analysis

Review:

- Trend
- Drawdowns
- Recovery periods
- Clusters of losses
- Clusters of wins
- Flat periods
- Regime dependence

A smooth aggregate metric can hide unstable behavior.

---

# 28. Drawdown Analysis

Record:

```text
Maximum Drawdown
Average Drawdown
Drawdown Duration
Recovery Time
Worst Period
```

Drawdown behavior is often more important than headline return.

---

# 29. Risk of Ruin

Evaluate whether plausible losing sequences can cause unacceptable capital impairment.

Consider:

- Risk per trade
- Win/loss distribution
- Trade frequency
- Correlation
- Drawdown
- Tail outcomes

---

# 30. Monte Carlo Analysis

Where appropriate, use Monte Carlo methods to explore uncertainty.

Potential approaches:

- Trade-order randomization
- Return resampling
- Slippage variation
- Parameter perturbation

Monte Carlo results should be presented as scenario analysis, not certainty.

---

# 31. Out-of-Sample Testing

A strategy should have data that was not used to develop or tune it.

Conceptually:

```text
Development Data
      ↓
Locked
      ↓
Final Evaluation Data
```

The final evaluation dataset should not repeatedly be used for tuning.

---

# 32. Train / Validation / Test

For models:

```text
Training Set
      ↓
Validation Set
      ↓
Test Set
```

The test set should remain protected until appropriate evaluation.

---

# 33. Walk-Forward Testing

For time series:

```text
Train → Test
     ↓
Shift
     ↓
Train → Test
     ↓
Shift
     ↓
Train → Test
```

This evaluates adaptation over changing market conditions.

---

# 34. Expanding vs Rolling Windows

TradeOS may support:

### Expanding

Historical training data grows over time.

### Rolling

Training uses a fixed recent window.

The appropriate approach depends on strategy/model assumptions.

---

# 35. Regime-Based Validation

Evaluate results by:

```text
Trending
Range
High Volatility
Low Volatility
Bull
Bear
Crisis
Recovery
```

A strategy should not be judged only by aggregate performance.

---

# 36. Market-Based Validation

Evaluate by:

- Market
- Asset class
- Instrument
- Sector
- Geography where relevant

A strategy that only works in one narrow environment should be labeled accordingly.

---

# 37. Time-Based Validation

Evaluate performance by:

- Time of day
- Day of week
- Month
- Year
- Session
- Holding period

This can reveal hidden dependencies.

---

# 38. Strategy Stability

A strategy should demonstrate reasonable stability across:

- Time
- Instruments
- Regimes
- Parameters
- Costs

Stability is generally more valuable than a single exceptional period.

---

# 39. Benchmarking

Strategies should be compared with appropriate benchmarks.

Depending on the strategy:

```text
Buy and Hold
Market Index
Cash
Risk-Free Reference
Alternative Strategy
```

Benchmark selection must be documented.

---

# 40. Prediction Model Validation

Prediction models require additional evaluation.

Measure:

- Accuracy where applicable
- Precision
- Recall
- Log loss
- Brier score
- Calibration
- Error by regime
- Error by horizon

Metrics should match the prediction problem.

---

# 41. Probability Calibration Validation

If a model predicts:

```text
70%
```

then comparable predictions should be evaluated against actual outcomes.

Track:

```text
Predicted Probability
Actual Frequency
Sample Size
Calibration Error
```

---

# 42. Agent Validation

Agents should be tested independently from trading P&L.

Evaluate:

- Output correctness
- Instruction following
- Structured output validity
- Abstention
- Hallucination rate
- Context use
- Repeated mistakes
- Tool use
- Latency
- Cost

---

# 43. Agent Scenario Tests

Create known test scenarios such as:

```text
Clean Setup
Conflicting Evidence
Missing Data
Stale Data
Extreme Volatility
Invalid Strategy
Risk Limit Breach
Ambiguous Instruction
```

The expected agent behavior should be defined before evaluation.

---

# 44. Agent Safety Tests

Agents should demonstrate that they:

- Do not bypass Risk
- Do not fabricate data
- Do not invent fills
- Do not override system controls
- Respect permissions
- Abstain when required
- Escalate uncertainty

---

# 45. Regression Testing

Every meaningful change should run regression tests.

Examples:

```text
Code Change
Prompt Change
Model Change
Strategy Change
Risk Change
Learning Rule Change
Schema Change
```

Existing safety behavior must remain intact.

---

# 46. Learning Rule Validation

Learning rules should be evaluated before activation.

Measure:

```text
Before Intervention
      vs
After Intervention
```

Potential outcomes:

```text
Improved
Neutral
Worse
Inconclusive
```

Learning recommendations and production learning changes must be evaluated using evidence independent of the data used to generate or tune the recommendation. A learning candidate must not contaminate the validation set that determines whether that candidate works.

---

# 47. False Intervention Rate

A learning rule may create unnecessary friction.

Track:

```text
Useful Interventions
vs
Unnecessary Interventions
```

An intervention that blocks too many good decisions may need modification.

---

# 48. Strategy Promotion Gates

Example framework:

```text
Backtest Passed
      ↓
Robustness Passed
      ↓
Out-of-Sample Passed
      ↓
Walk-Forward Passed
      ↓
Paper Passed
      ↓
Review
      ↓
Production Candidate
```

Exact thresholds belong in configuration/governance, not hard-coded prose.

Passing validation makes an artifact eligible for the next governance stage; it does not itself grant live trading authority.

---

# 49. Paper Trading

Paper trading should approximate live operation.

It should exercise:

- Market data
- Agents
- Risk
- Execution simulation
- Portfolio state
- Journaling
- Learning

Paper results should be clearly labeled as simulated.

---

# 50. Paper-to-Live Review

Before live promotion, review:

```text
Strategy Performance
Risk Behavior
Execution Assumptions
Data Quality
Agent Reliability
Prediction Calibration
Operational Stability
Learning Behavior
```

---

# 51. Controlled Production

Production deployment should be staged.

Possible progression:

```text
Tiny Capital
      ↓
Limited Exposure
      ↓
Observation
      ↓
Increase Within Limits
```

Production limits should remain governed by Risk.

---

# 52. Canary Deployment

New strategies, models, or agents may use controlled canary exposure.

Examples:

```text
New Model → Small Allocation
New Strategy → Paper
New Agent → Shadow Mode
```

---

# 53. Shadow Mode

A component may operate without affecting decisions.

Example:

```text
New Prediction Model
      ↓
Shadow Prediction
      ↓
Compare Against Production
```

This provides real-world evidence without immediate financial authority.

---

# 54. Promotion Approval

Production promotion should require documented approval according to the governance model.

The approval record should contain:

- Artifact version
- Validation results
- Known limitations
- Risk assessment
- Approval identity
- Timestamp

Validation evidence supports the approval record; validation itself is not the approval authority.

---

# 55. Rollback

Every production artifact should have a rollback path.

```text
Current Version
      ↓
Problem Detected
      ↓
Disable / Rollback
      ↓
Previous Validated Version
```

Rollback must be tested.

---

# 56. Validation Failure

A failed validation should not be hidden.

Possible statuses:

```text
PASSED
FAILED
INCONCLUSIVE
REQUIRES_REVIEW
```

Negative results should remain in the research record.

---

# 57. Research Registry

TradeOS should maintain a registry of experiments.

Each experiment should track:

```text
experiment_id
hypothesis
artifact
version
dataset
parameters
metrics
result
status
conclusion
```

---

# 58. Experiment Lineage

A production strategy should be traceable to its research lineage.

```text
Production Strategy
      ↓
Approved Version
      ↓
Paper Version
      ↓
Validation
      ↓
Backtest
      ↓
Research Experiment
```

---

# 59. Validation Evidence

Important promotion decisions should reference evidence.

Avoid statements such as:

> "The strategy looks good."

Prefer:

```text
Out-of-Sample:
X trades

Max Drawdown:
Y

Profit Factor:
Z

Walk-Forward:
Passed

Paper:
N sessions

Known Weakness:
High-volatility range markets
```

---

# 60. Avoiding Backtest Optimization Loops

A dangerous process is:

```text
Backtest
 ↓
Tune
 ↓
Backtest
 ↓
Tune
 ↓
Backtest
 ↓
Tune
```

against the same evaluation data.

TradeOS should protect final evaluation datasets.

---

# 61. Validation Budget

Research may have limits on:

- Number of experiments
- Compute
- Model calls
- Dataset size
- Parameter searches

This reduces uncontrolled optimization.

Validation budgets should be used to prioritize the tests most informative for the artifact and decision at hand, rather than maximizing the number of tests performed.

---

# 62. Statistical Significance

Where applicable, evaluate whether observed results could reasonably arise from chance.

Do not use statistical significance as the only approval criterion.

Economic significance and practical robustness also matter.

---

# 63. Sample Size

Small samples should be labeled.

Example:

```text
12 trades
```

should not receive the same confidence as:

```text
1,200 trades
```

TradeOS should expose sample size alongside performance metrics.

---

# 64. Confidence Intervals

Where useful, provide uncertainty around estimates such as:

- Win rate
- Expectancy
- Return
- Sharpe
- Prediction accuracy

---

# 65. Data Snooping

Research workflows should minimize repeated inspection of the final test set.

Test-set contamination should trigger a lower-confidence evaluation status.

---

# 66. Validation of Risk Controls

Risk controls themselves must be tested.

Examples:

```text
Position Size Limit
Daily Loss Limit
Drawdown Halt
Leverage Limit
Margin Limit
Kill Switch
```

Test:

```text
Below Threshold
At Threshold
Above Threshold
```

Validation of risk controls demonstrates their behavior under test conditions. It does not replace live risk authorization.

---

# 67. Validation of Execution Controls

Test:

- Duplicate order prevention
- Unknown order state
- Partial fill
- Broker rejection
- Timeout
- Network failure
- Reconciliation

---

# 68. Validation of Data Controls

Test:

- Missing data
- Stale data
- Duplicate data
- Out-of-order events
- Invalid prices
- Provider outage

The expected safety response must be defined.

---

# 69. Validation of Learning Controls

Test that:

```text
Mistake
 ↓
Pattern
 ↓
Learning Candidate
```

does not automatically become:

```text
Production Rule
```

without validation and governance.

Learning candidates must remain separated from protected evaluation evidence when that evidence is used to determine whether the candidate is effective.

---

# 70. Validation Environment Separation

Where practical, maintain:

```text
Development
Testing
Research
Paper
Production
```

with controlled promotion paths.

---

# 71. Production Data Feedback

Production and paper outcomes should feed evaluation.

```text
Production
   ↓
Outcome
   ↓
Performance
   ↓
Drift
   ↓
Review
```

Production success does not eliminate the need for continued validation.

---

# 72. Continuous Validation

Validation should continue after deployment.

Monitor:

- Performance
- Risk
- Calibration
- Drift
- Execution
- Agent behavior
- Data quality

---

# 73. Drift Detection

Potential drift includes:

```text
Market Drift
Feature Drift
Model Drift
Strategy Drift
Execution Drift
Behavioral Drift
```

A drift signal should trigger investigation rather than automatic conclusions.

---

# 74. Revalidation Triggers

Revalidation may be required after:

- Major code change
- Model change
- Strategy change
- Risk change
- Data provider change
- Market regime shift
- Significant performance degradation
- Learning rule change

---

# 75. Validation and Learning

Validation results should feed the Learning System.

Example:

```text
Strategy Failed in Regime X
      ↓
Pattern
      ↓
Learning Candidate
      ↓
Research
      ↓
Validation
```

Learning does not bypass validation.

Validation evidence should remain separated from any learning process that could tune the artifact against that same evidence.

---

# 76. Validation Architecture Invariants

The following must remain true:

1. Backtests are evidence, not proof.
2. Final test data must be protected.
3. No look-ahead bias.
4. No uncontrolled data leakage.
5. Costs and slippage must be realistic.
6. Sample size must be visible.
7. Robustness matters more than a single optimized result.
8. Negative research results are preserved.
9. Production artifacts are versioned.
10. Every production artifact has a rollback path.
11. Agents must pass safety tests.
12. Risk controls must be independently tested.
13. Learning rules require validation.
14. Validation cannot be bypassed by an agent.
15. Production performance must continue to be monitored.
16. Validation establishes evidence and promotion eligibility but does not itself authorize live trading.
17. Protected evaluation evidence must not be used to tune the artifact being evaluated.
18. Validation depth should be proportionate to evidence, uncertainty, impact, and promotion risk.
19. Validation workflows must not create unbounded agent coordination loops.

---

# 77. Initial Validation Implementation

The first implementation should focus on:

```text
Strategy
 ↓
Backtest
 ↓
Trade-Level Results
 ↓
Basic Metrics
 ↓
Parameter Sensitivity
 ↓
Out-of-Sample
 ↓
Paper
 ↓
Review
```

Then add:

```text
Walk-Forward
Monte Carlo
Regime Analysis
Prediction Calibration
Agent Evaluation
Learning Intervention Experiments
Continuous Drift Detection
```

Deeper validation should be introduced when it answers a material question about robustness, uncertainty, or promotion—not merely because another test is available.

---

# 78. Validation Architecture Success Criteria

The system is successful when TradeOS can:

- Reproduce backtests.
- Detect data leakage.
- Evaluate realistic costs.
- Measure strategy robustness.
- Protect out-of-sample data.
- Test agents independently.
- Validate risk controls.
- Validate learning interventions.
- Promote artifacts through controlled gates.
- Roll back production changes.
- Continuously monitor deployed systems.
- Distinguish validation evidence from live authorization.
- Preserve independence between learning/tuning and protected evaluation evidence.
- Scale validation depth efficiently according to the question and risk.

---

# 79. Related Documents

- `README.md`
- `rules.md`
- `docs/01_PROJECT_VISION.md`
- `docs/02_DESIGN_PRINCIPLES.md`
- `docs/03_ENGINEERING_PRINCIPLES.md`
- `docs/04_SYSTEM_ARCHITECTURE.md`
- `docs/05_AGENT_ARCHITECTURE.md`
- `docs/06_DATA_ARCHITECTURE.md`
- `docs/07_TRADING_WORKFLOWS.md`
- `docs/08_RISK_MANAGEMENT.md`
- `docs/09_PREDICTION_ENGINE.md`
- `docs/10_LEARNING_SYSTEM.md`
- `docs/12_EXECUTION_ARCHITECTURE.md`
- `docs/20_AGENT_CONTRACTS.md`
- `docs/21_CONFIGURATION.md`

---

## Version History

| Version | Status | Description |
|---|---|---|
| 0.1.0 | Architecture Baseline | Initial TradeOS backtesting and validation architecture, including robustness, out-of-sample testing, agent validation, learning validation, and controlled promotion |
| 0.2.0 | Architecture Baseline | Aligned validation authority, protected evaluation evidence, efficient validation depth, and risk/learning boundaries |

---

> **Validation principle: test honestly, protect the evidence, model reality conservatively, and never promote what has not earned trust.**
