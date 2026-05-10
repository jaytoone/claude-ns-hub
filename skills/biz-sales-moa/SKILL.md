---
name: biz-sales-moa
description: "BIZ/SALES MOA — Integrated utilization of 12 business/sales agents. Routes N agents by problem type or allows full selection. Parallel analysis followed by integrated synthesis using MoA (Mixture of Agents) pattern."
trigger: manual
tags:
  - sales
  - moa
  - multi-agent
  - business-strategy
  - growth
  - conversion
---

# BIZ/SALES MOA Protocol

MoA (Mixture of Agents) analysis system leveraging 12 BIZ/SALES specialized agents.

---

## Step 0: 12 Agent Feature Overview

| # | Agent | Core Domain | Key Perspective |
|---|-------|------------|-----------------|
| 1 | `biz-sales` | B2B sales/customer acquisition | Marketing strategy, funnel optimization |
| 2 | `biz-strategy` | Business strategy/competitive advantage | Revenue model, market positioning |
| 3 | `biz-gap-theory` | GAP analysis | Current vs target gap, prioritization |
| 4 | `review-harsh-critic` | Critical review | Weaknesses/assumption errors/lack of numerical evidence |
| 5 | `biz-aarrr-funnel` | AARRR funnel | Acquisition~Revenue~Referral |
| 6 | `biz-plg` | PLG growth | Aha Moment, PQL, Free→Paid conversion |
| 7 | `biz-growth-loop` | Growth loops | Self-reinforcing structure, data flywheel |
| 8 | `biz-gtm` | Market entry | ICP, channel strategy |
| 9 | `biz-bmc` | Business model | 9-block consistency |
| 10 | `biz-flywheel` | Flywheel | Economies of scale, competitive moat |
| 11 | `biz-ai-monetization` | AI monetization | Pricing Metric, Usage-based |
| 12 | `biz-unconscious-purchase` | Unconscious purchase | System 1/2, SPIKE, Cialdini |

---

## Step 1: Problem Type → Agent Selection Matrix

### Automatic Routing (keyword-based)

| Problem Keywords | Selected Agents (4~6) |
|-----------------|----------------------|
| "conversion rate", "subscription", "paid conversion" | PLG + AARRR + Unconscious Purchase + Sales |
| "growth", "churn", "user increase" | AARRR + Growth Loop + Gap Theory |
| "monetization", "pricing", "margin" | AI Monetization + PLG + Business Strategy |
| "competition", "moat", "differentiation" | Flywheel + Growth Loop + BMC |
| "customer acquisition", "inflow", "channel" | GTM + Sales + AARRR |
| "business model", "consistency" | BMC + AI Monetization + Business Strategy |
| "marketing", "persuasion", "brand" | Unconscious Purchase + Sales + Business Strategy |

### Manual Selection (user request)

```
If user says "use all" or specifies agents → run all 12 in parallel
```

---

## Step 2: Parallel Analysis Execution

### 4 Agents (standard)

```
Task(subagent_type="general-purpose", run_in_background=True,
  prompt="Analyze only from the [Agent1] expert perspective. Ignore other perspectives.

{problem}

### Key Findings (3+, with measurable metrics)
### Biggest Risk (1, with specific evidence)
### Immediately Actionable Prescription (something you can do today)")

Task(subagent_type="general-purpose", run_in_background=True,
  prompt="Analyze only from the [Agent2] expert perspective. ...")
```

### 6 Agents (extended)

```
Task(subagent_type="general-purpose", run_in_background=True, prompt=...)
Task(subagent_type="general-purpose", run_in_background=True, prompt=...)
Task(subagent_type="general-purpose", run_in_background=True, prompt=...)
Task(subagent_type="general-purpose", run_in_background=True, prompt=...)
Task(subagent_type="general-purpose", run_in_background=True, prompt=...)
Task(subagent_type="general-purpose", run_in_background=True, prompt=...)
```

### 12 Agents (full)

```
Task(subagent_type="general-purpose", run_in_background=True, prompt=...) # repeat 12 times
```

---

## Step 3: Integrated Synthesis

### After collecting agent results:

1. **Cross blind spot extraction**: Items flagged by 2+ agents simultaneously
2. **Tradeoff statement**: Conflicts between frameworks
3. **Top action items**: 3 things you can do today
4. **6-month pivot signals**: Success conditions by metric

---

## Output Format

```
### Selected Agents: N
### Selection Rationale: [Problem type/keywords]

---
### Cross Blind Spots (flagged by multiple agents simultaneously)
...

### Integrated Recommendations
...

### Tradeoffs
...

### Top 3 Action Items (today)
1. ...
2. ...
3. ...

### 6-Month Pivot Signals
- When [metric] achieved → [next step]
```

---

## Quality Check

- [ ] Are selected agents relevant to the problem?
- [ ] Are there 2+ cross blind spots?
- [ ] Are Top 3 items executable today?
- [ ] Are 6-month pivot signals clear?

---

## Usage Examples

### Example 1: Conversion Rate Problem (4 agents)
```
Problem: "Our paid subscription conversion rate is 0%. How can we improve it?"
→ Select PLG + AARRR + Unconscious Purchase + Sales
```

### Example 2: Growth Problem (6 agents)
```
Problem: "User growth has stalled. How can we restart growth?"
→ AARRR + Growth Loop + GTM + Gap Theory + Sales + Business Strategy
```

### Example 3: Full Analysis (12 agents)
```
Problem: "Analyze all business problems for PaintPoint"
→ Run all 12 agents in parallel
```

---

## Documentation Obligation (MANDATORY)

After pipeline execution, **agent responses and final conclusions must be saved as a document**. Skipping documentation means the pipeline is considered **incomplete**.

### Saving Rules

1. **Save path**: `docs/research/[YYYYMMDD]-[topic-summary].md` (project docs folder)
2. **Save timing**: **Immediately before** returning the final answer to the user
3. **DOC_INDEX.md update**: Register in the `docs/DOC_INDEX.md` top table after saving
4. **Content to save**:

```markdown
# [biz-sales-moa] {Topic Summary}
**Date**: {YYYY-MM-DD}  **Skill**: biz-sales-moa

## Original Problem
{problem}

## Selected Agents: {N}
{Selection rationale + agent list}

## Agent Response Summary
{Key findings + risks + recommendations summary for each agent}

## Cross Blind Spots
{Items flagged by 2+ agents simultaneously}

## Final Conclusion
{Integrated recommendations + Top 3 action items + 6-month pivot signals}
```
