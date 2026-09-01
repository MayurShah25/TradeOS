# TradeOS Research Architecture

**Document:** 15_RESEARCH_ARCHITECTURE.md  
**Version:** 0.1.0  
**Status:** Architecture Baseline  
**Scope:** Research lifecycle, hypotheses, experiments, datasets, features, parameter studies, research agents, evidence, reproducibility, and promotion to validation

---

## 1. Purpose

The Research Architecture defines how TradeOS turns an idea into structured, reproducible evidence.

The core principle is:

> **Research produces hypotheses and evidence; validation determines whether the evidence is strong enough for promotion.**

Research must remain separate from production trading authority.

---

# 2. Research Philosophy

TradeOS should distinguish:

```text
Idea
  ≠
Hypothesis
  ≠
Experiment
  ≠
Result
  ≠
Validated Finding
  ≠
Production Strategy
```

A compelling research result is not automatically a production-ready strategy.

---

# 3. Research Lifecycle

```text
Observation
   ↓
Idea
   ↓
Hypothesis
   ↓
Experiment Design
   ↓
Data Selection
   ↓
Implementation
   ↓
Experiment
   ↓
Analysis
   ↓
Replication
   ↓
Validation
   ↓
Promotion / Rejection
```

---

# 4. Research Registry

TradeOS should maintain a registry of research activities.

Each research item should have:

```text
research_id
title
description
hypothesis
status
owner
created_at
updated_at
```

---

# 5. Research Status

Possible statuses:

```text
IDEA
HYPOTHESIS
DESIGN
RUNNING
ANALYSIS
REPLICATION
VALIDATION
PROMOTED
REJECTED
ABANDONED
```

---

# 6. Hypothesis

A hypothesis should be explicit and testable.

Example:

> "A breakout accompanied by unusually high relative volume may produce better forward returns under specified market conditions."

The hypothesis should define:

- Population
- Conditions
- Expected behavior
- Measurement
- Time horizon

---

# 7. Falsifiability

A useful research hypothesis should be capable of being disproven.

Avoid:

> "This strategy seems to work."

Prefer:

> "Under condition X, outcome Y is expected to exceed baseline Z by a defined amount."

---

# 8. Research Question

Every experiment should identify the question it is attempting to answer.

Examples:

```text
Does volatility affect breakout expectancy?

Does prediction confidence improve trade selection?

Does a risk reduction rule reduce drawdown?

Does a learning intervention reduce repeated mistakes?
```

---

# 9. Baseline

Experiments should have an appropriate baseline.

Examples:

```text
Strategy vs Buy-and-Hold
Strategy vs Existing Version
Model A vs Model B
Intervention vs No Intervention
```

Without a baseline, improvement is difficult to establish.

---

# 10. Experiment Definition

An experiment should define:

```text
experiment_id
research_id
hypothesis
dataset
strategy/model version
parameters
evaluation metrics
random seed where applicable
created_at
```

---

# 11. Experiment Immutability

Once an experiment begins, its defining inputs should be preserved.

If parameters change materially:

```text
Experiment A
      ↓
Experiment B
```

rather than silently editing Experiment A.

---

# 12. Dataset Selection

Research must record:

```text
dataset_id
dataset_version
provider
date range
universe
adjustment policy
point-in-time policy
```

---

# 13. Data Eligibility

The research system should verify that data is appropriate for the question.

Consider:

- Coverage
- Quality
- Point-in-time availability
- Revisions
- Missing values
- Survivorship
- Corporate actions

---

# 14. Feature Registry

Research features should be registered.

Potential fields:

```text
feature_id
feature_version
description
inputs
formula
availability
owner
status
```

---

# 15. Feature Lineage

Every research feature should be traceable to its source inputs.

```text
Raw Data
   ↓
Transformation
   ↓
Feature
   ↓
Model / Strategy
   ↓
Experiment
```

---

# 16. Experiment Parameters

Parameters should be explicit.

Example:

```text
lookback
threshold
holding_period
stop_distance
position_size
```

Do not hide parameters inside code.

---

# 17. Parameter Search

Parameter exploration may use:

```text
Grid Search
Random Search
Bayesian Search
Manual Research
```

The search process should be recorded.

---

# 18. Parameter Search Risk

Large parameter searches increase overfitting risk.

TradeOS should record:

```text
parameter combinations tested
selection criteria
best result
distribution of results
```

Do not report only the best configuration.

---

# 19. Parameter Stability

Research should examine whether nearby parameter values produce similar outcomes.

Stable regions are generally more trustworthy than isolated peaks.

---

# 20. Experiment Reproducibility

A research experiment should be reproducible from:

```text
Code Version
Dataset Version
Feature Version
Configuration Version
Parameters
Random Seed
Environment
```

---

# 21. Experiment Lineage

Research lineage should look like:

```text
Research Idea
    ↓
Hypothesis
    ↓
Experiment
    ↓
Result
    ↓
Replication
    ↓
Validation
    ↓
Strategy Version
```

---

# 22. Research Notebook

Researchers may use notebooks for exploration.

However, important conclusions should eventually become reproducible code and registered experiments.

Notebook-only results should not be treated as production evidence.

---

# 23. Research Code

Research code should remain distinguishable from production code.

Potential structure:

```text
research/
├── hypotheses/
├── experiments/
├── notebooks/
├── datasets/
├── reports/
└── utilities/
```

Exact implementation may evolve.

---

# 24. Research Environment

Research should use a controlled environment.

Record:

```text
runtime version
dependencies
hardware where material
model versions
data versions
```

---

# 25. Experiment Output

An experiment should produce structured results.

Example:

```text
experiment_id
metrics
trade_count
period
drawdown
return
error_metrics
confidence
artifacts
```

---

# 26. Research Artifacts

Artifacts may include:

- Reports
- Charts
- Model files
- Feature sets
- Backtest outputs
- Statistical results
- Experiment logs

Artifacts should be versioned or linked to the experiment.

---

# 27. Negative Results

Failed experiments must be retained.

A research system should be able to answer:

> "What have we already tried?"

This prevents repeatedly pursuing known failures.

---

# 28. Research Knowledge Base

Validated research findings may become searchable knowledge.

However:

```text
Research Finding
      ≠
Production Rule
```

Promotion requires validation and governance.

---

# 29. Research Agent

The Research Agent may:

- Search for ideas
- Form hypotheses
- Design experiments
- Analyze results
- Compare approaches
- Identify gaps
- Recommend next experiments

It must not directly deploy production strategies.

---

# 30. Research Agent Evidence

Research Agent conclusions should reference:

```text
data
experiments
sources
assumptions
limitations
```

---

# 31. Research Agent Boundaries

The Research Agent must not:

- Fabricate research results
- Claim an experiment was run when it was not
- Modify production strategies
- Change risk limits
- Promote its own work

---

# 32. Research and External Information

External information should be treated as research input.

Examples:

- Academic papers
- Market studies
- Public documentation
- News
- Industry reports

External claims should be distinguished from TradeOS experimental evidence.

---

# 33. Research Source Registry

Where useful, record:

```text
source_id
source_type
title
publisher
publication_date
retrieved_at
reference
```

---

# 34. Literature Review

Research may include literature reviews to identify:

- Existing methods
- Known weaknesses
- Common biases
- Alternative approaches
- Replication opportunities

A literature claim is not equivalent to internal validation.

---

# 35. Research Replication

Promising findings should be replicated.

Possible replication dimensions:

```text
Different Period
Different Instrument
Different Market
Different Parameters
Different Data Sample
```

---

# 36. Cross-Market Research

A strategy may appear successful in one market.

Research should determine whether the finding generalizes.

Results should clearly state scope.

---

# 37. Regime Research

Research should test behavior under different regimes.

Examples:

```text
Trend
Range
High Volatility
Low Volatility
Crisis
Recovery
```

---

# 38. Counterfactual Research

Research may examine:

> What might have happened under a different decision?

Counterfactual results must remain separate from actual historical outcomes.

---

# 39. Causal Research

Where appropriate, research may investigate causality.

Potential methods may include:

- Controlled experiments
- Natural experiments
- Statistical causal methods

Causal claims require stronger evidence than correlation.

---

# 40. Research Metrics

Metrics should match the research question.

Examples:

```text
Return
Drawdown
Expectancy
Calibration
Accuracy
Latency
Error Rate
Execution Cost
```

---

# 41. Statistical Testing

Where appropriate, research may use:

- Confidence intervals
- Hypothesis tests
- Bootstrap methods
- Permutation tests
- Monte Carlo methods

Statistical significance should not replace economic/practical significance.

---

# 42. Economic Significance

A statistically detectable effect may be too small to trade after:

```text
Fees
Slippage
Latency
Market Impact
```

Research must consider practical implementation.

---

# 43. Multiple Hypotheses

When many hypotheses are tested, the research record should make that visible.

Avoid presenting one successful result without its broader experiment context.

---

# 44. Research Selection Bias

Document:

- Why a dataset was selected
- Why an instrument was selected
- Why a period was selected
- Why a strategy was selected

---

# 45. Research Data Snooping

Repeatedly inspecting evaluation data can contaminate the evidence.

Research should preserve a protected evaluation process.

---

# 46. Research Experiment Groups

Related experiments may be grouped:

```text
Experiment Family
    ├── v1
    ├── v2
    ├── v3
    └── v4
```

This allows the complete search history to be evaluated.

---

# 47. Research Champion Bias

The system should avoid selecting only the strongest researcher/model result.

Research governance should consider:

```text
All Relevant Experiments
```

not only the winner.

---

# 48. Research Review

Promising findings should undergo review.

Review should examine:

```text
Hypothesis
Data
Method
Results
Bias
Robustness
Limitations
Replication
```

---

# 49. Promotion to Validation

A research result may become a validation candidate when:

- Hypothesis is clear
- Experiment is reproducible
- Results are meaningful
- Major biases are addressed
- Robustness is reasonable
- Scope is understood

---

# 50. Promotion Record

Record:

```text
research_id
experiment_id
candidate_version
promotion_reason
known_limitations
reviewer
timestamp
```

---

# 51. Research Rejection

A result may be rejected because:

```text
Insufficient Evidence
Overfitting
Data Problems
Weak Effect
Poor Robustness
Operational Impracticality
Risk Concerns
```

The rejection should remain recorded.

---

# 52. Research Retirement

Ideas can be retired.

Retirement does not mean:

> "This can never work."

It means:

> "Current evidence does not justify further active development."

---

# 53. Research Resumption

A retired hypothesis may be reopened if:

- New data becomes available
- Market structure changes
- New methodology emerges
- New evidence appears

The lineage should remain connected.

---

# 54. Research and Backtesting

Research generates candidates.

Backtesting evaluates candidates under the defined validation framework.

```text
Research
   ↓
Candidate
   ↓
Backtesting
```

---

# 55. Research and Strategy

A research result may create a strategy version.

```text
Research Finding
      ↓
Strategy Definition
      ↓
Validation
      ↓
Candidate
```

The strategy must not skip validation.

---

# 56. Research and Prediction

Research may produce:

- Features
- Models
- Prediction hypotheses
- Calibration methods

Prediction artifacts must still pass model validation.

---

# 57. Research and Learning

The Learning System may generate research questions.

Example:

```text
Repeated Failure Pattern
      ↓
Research Question
      ↓
Experiment
      ↓
Potential Intervention
```

---

# 58. Research and Portfolio

Research may investigate:

- Allocation
- Diversification
- Correlation
- Position sizing
- Portfolio construction

Portfolio changes remain governed by Risk.

---

# 59. Research and Execution

Research may investigate:

- Order types
- Slippage
- Market impact
- Execution timing
- Broker behavior

Execution changes must pass execution validation.

---

# 60. Research and Configuration

Research parameters should be explicit and versioned.

A research result should identify the configuration used.

---

# 61. Research Experiment Security

Research environments must not accidentally have production execution privileges.

A research agent should not be able to submit live orders.

---

# 62. Research Cost Controls

Research may consume:

- Compute
- API calls
- Data
- Model tokens
- Storage

Budgets should prevent uncontrolled experimentation.

---

# 63. Research Queue

TradeOS may maintain a prioritized research queue.

Priority can consider:

```text
Expected Value
Safety Impact
Research Cost
Evidence Quality
Strategic Importance
```

---

# 64. Research Automation

Some experiments may run automatically.

Automated research must still:

- Record inputs
- Record outputs
- Preserve lineage
- Respect data boundaries
- Respect compute budgets

---

# 65. Research Scheduling

Research jobs should have explicit:

```text
priority
dependencies
resource requirements
timeout
status
```

---

# 66. Research Reproducibility Test

Before promotion, TradeOS should be able to rerun the experiment or reproduce its material results.

If not:

```text
REQUIRES_REVIEW
```

---

# 67. Research Report

A research report should include:

```text
Question
Hypothesis
Data
Method
Experiments
Results
Limitations
Conclusion
Next Step
```

---

# 68. Research Confidence

Research conclusions should include confidence or evidence strength where appropriate.

Example:

```text
Evidence:
Moderate

Replication:
2/3 periods

Major Limitation:
Small sample
```

---

# 69. Research Uncertainty

Research should explicitly state:

- Unknowns
- Assumptions
- Data limitations
- Generalization limitations

---

# 70. Research Governance

No Research Agent or researcher should be able to:

```text
Research
 ↓
Production
```

without the defined validation and approval path.

---

# 71. Research Audit Trail

Preserve:

```text
Who created hypothesis
Who ran experiment
What data was used
What parameters were tested
What result occurred
What conclusion was reached
Who approved promotion
```

---

# 72. Research Architecture Invariants

The following must remain true:

1. Research is separate from production authority.
2. Hypotheses are explicit.
3. Experiments are reproducible.
4. Data versions are recorded.
5. Feature versions are recorded.
6. Parameters are visible.
7. Negative results are preserved.
8. Search history is not hidden.
9. Test/evaluation contamination is controlled.
10. Research agents cannot deploy production strategies.
11. Research findings do not automatically become rules.
12. External claims are distinct from internal evidence.
13. Promotion requires validation.
14. Research lineage is preserved.
15. Research cannot bypass Risk or Execution controls.

---

# 73. Initial Research Implementation

The first implementation should support:

```text
Research Idea
 ↓
Hypothesis
 ↓
Experiment Definition
 ↓
Dataset
 ↓
Backtest
 ↓
Result
 ↓
Research Report
```

Then add:

```text
Experiment Registry
Parameter Search
Replication
Research Agent
Research Queue
Automated Experiments
Research Knowledge Base
```

---

# 74. Research Architecture Success Criteria

The Research System is successful when TradeOS can:

- Record ideas systematically.
- Form testable hypotheses.
- Run reproducible experiments.
- Track datasets and features.
- Track parameter searches.
- Preserve failed experiments.
- Compare results against baselines.
- Identify robust findings.
- Promote promising research into validation.
- Maintain complete research lineage.
- Prevent research from directly affecting production.

---

# 75. Related Documents

- `README.md`
- `rules.md`
- `docs/04_SYSTEM_ARCHITECTURE.md`
- `docs/05_AGENT_ARCHITECTURE.md`
- `docs/06_DATA_ARCHITECTURE.md`
- `docs/09_PREDICTION_ENGINE.md`
- `docs/10_LEARNING_SYSTEM.md`
- `docs/11_BACKTESTING_AND_VALIDATION.md`
- `docs/13_PORTFOLIO_ARCHITECTURE.md`
- `docs/14_MARKET_DATA_ARCHITECTURE.md`
- `docs/16_STRATEGY_ARCHITECTURE.md`
- `docs/20_AGENT_CONTRACTS.md`
- `docs/21_CONFIGURATION.md`

---

## Version History

| Version | Status | Description |
|---|---|---|
| 0.1.0 | Architecture Baseline | Initial TradeOS research architecture, including hypotheses, experiments, reproducibility, research agents, evidence, lineage, and controlled promotion |

---

> **Research principle: ask a precise question, test it honestly, preserve what you learned—even when the answer is no—and promote only what survives disciplined validation.**
