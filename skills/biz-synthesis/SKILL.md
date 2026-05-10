---
name: biz-synthesis
description: "Multi-angle business problem analysis (MAD variant) — Round 1: biz-sales/biz-strategy/biz-gap-theory independent parallel analysis. Round 2: review-harsh-critic reads all 3 results and attacks weaknesses/assumption errors. Synthesis produces verified final insights."
trigger: manual
tags:
  - business
  - strategy
  - sales
  - multi-agent
  - mad
  - critique
---

# Business Synthesis Protocol (MAD Variant)

Processes business/strategy/sales problems with 3 specialized agent analyses + review-harsh-critic verification.

Rationale: MAD (Liang et al. 2023) — Round 2 cross-critique has higher error detection rate than simple synthesis.

---

## Round 1: Parallel Independent Analysis (must be in a single response block)

3 agents analyze independently without knowledge of each other's outputs:

```
Task(subagent_type="biz-sales", run_in_background=True,
  prompt="Analyze only from the sales/channel/customer acquisition/pipeline perspective. Ignore other perspectives.

{problem}

### Key Findings (3+, with specific evidence)
### Biggest Sales Risk
### Immediately Actionable Recommendations")

Task(subagent_type="biz-strategy", run_in_background=True,
  prompt="Analyze only from the business strategy/competitive advantage/revenue model/market positioning perspective. Ignore other perspectives.

{problem}

### Key Findings (3+, with specific evidence)
### Biggest Strategic Risk
### Immediately Actionable Recommendations")

Task(subagent_type="biz-gap-theory", run_in_background=True,
  prompt="Analyze the gap between current state and target using GAP theory. Ignore other perspectives.

{problem}

### Key GAP Findings (3+, with quantitative evidence)
### Most Critical Gap
### Immediately Actionable Recommendations")
```

---

## Round 2: Dedicated review-harsh-critic Verification (sequential after Round 1 completion)

review-harsh-critic reads all 3 Round 1 results and attacks weaknesses:

```
Task(subagent_type="review-harsh-critic",
  prompt="Ruthlessly critique the weaknesses, assumption errors, and lack of numerical evidence in the 3 business analysis results below.

=== biz-sales Analysis ===
{sales_result}

=== biz-strategy Analysis ===
{strategy_result}

=== biz-gap-theory Analysis ===
{gap_result}

### Critical Weaknesses of Each Analysis (with evidence)
### Common Blind Spots Missed by All 3 Analyses
### List of Assumptions That Will Fail If Executed Without Correction")
```

---

## Synthesis: Deriving Final Insights

Combine Round 1 (3 analyses) + Round 2 (review-harsh-critic critique):

1. Weaknesses identified by review-harsh-critic → address first
2. Items flagged by 2+ agents simultaneously → cross blind spots (highest priority)
3. When conflicts exist, state tradeoffs explicitly
4. Only verified recommendations in the final output

---

## Output Format

```
### Cross Blind Spots (flagged by 2+ agents simultaneously)
...

### Key Issues Raised by review-harsh-critic
...

### Verified Final Recommendations
...

### Residual Risks (unresolved)
...
```

---

## Quality Check

Verify before synthesis:
- [ ] Have review-harsh-critic's critiques been reflected in the final recommendations?
- [ ] Are cross blind spots explicitly stated?
- [ ] Have unsupported assumptions been removed?

If any is No → re-run synthesis

---

## Documentation Obligation (MANDATORY)

After pipeline execution, **agent responses and final conclusions must be saved as a document**. Skipping documentation means the pipeline is considered **incomplete**.

### Saving Rules

1. **Save path**: `docs/research/[YYYYMMDD]-[topic-summary].md` (project docs folder)
2. **Save timing**: **Immediately before** returning the final answer to the user
3. **DOC_INDEX.md update**: Register in the `docs/DOC_INDEX.md` top table after saving
4. **Content to save**:

```markdown
# [biz-synthesis] {Topic Summary}
**Date**: {YYYY-MM-DD}  **Skill**: biz-synthesis

## Original Problem
{problem}

## Agent Response Summary
### biz-sales
{Key findings from sales/channel/customer acquisition perspective}

### biz-strategy
{Key findings from strategy/competitive advantage/revenue model perspective}

### biz-gap-theory
{Key findings from GAP analysis}

### review-harsh-critic
{Summary of weakness/assumption error attacks}

## Cross Blind Spots
{Items flagged by 2+ agents simultaneously}

## Final Conclusion
{Verified final recommendations + residual risks}
```
