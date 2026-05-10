---
name: bs-framework-synthesis
description: "BS Framework dynamic orchestration — Problem classification → Auto-select 2~3 frameworks → Parallel specialized agent analysis → biz-framework-integrator synthesis. BS Framework-specific version of biz-synthesis."
trigger: manual
tags:
  - business
  - strategy
  - bs-framework
  - multi-agent
  - orchestration
---

# BS Framework Synthesis Protocol

Auto-classify business problems → Select 2~3 relevant BS frameworks → Run specialized agents in parallel → Integrated synthesis.

Rationale: MoA (Mixture of Agents, Together AI 2024) — Independent expert parallel analysis has higher cross blind spot detection rate than single agent.

---

## Step 0: Problem Classification → Framework Selection

Internal reasoning (not output):

```
Startup stage determination:
  Pre-seed  → BMC + GTM
  Seed      → AARRR + PLG + GTM (pick 2)
  PMF confirmed  → AARRR + Growth Loop
  Series A  → Growth Loop + Flywheel + PLG (pick 2)
  Series B+ → Flywheel + AI Monetization

Core problem type:
  Growth bottleneck    → AARRR + Growth Loop
  Monetization         → AI Monetization + PLG
  Market entry         → GTM + BMC
  Structure/moat       → Flywheel + Growth Loop
  Product strategy     → PLG + AARRR
  Business model       → BMC + AI Monetization
```

State the selected 2~3 agents at the very top of the output:
```
Selected frameworks: [A] + [B] (+ [C])
Selection rationale: [Startup stage] / [Core problem type]
```

---

## Step 1: Parallel Independent Analysis (must be in a single response block)

Run selected agents simultaneously. Each analyzes independently without knowledge of others' outputs:

### Framework-to-Agent Mapping

> ⚠️ Custom agents cannot be called directly via Task subagent_type.
> All use `general-purpose` + embed agent file content into the prompt.
> Agent file path: `~/.claude/agents/[name].md`

| Framework | Agent File | subagent_type |
|-----------|-----------|--------------|
| AARRR Funnel | `biz-aarrr-funnel.md` | `general-purpose` |
| BMC | `biz-bmc.md` | `general-purpose` |
| GTM | `biz-gtm.md` | `general-purpose` |
| Growth Loop | `biz-growth-loop.md` | `general-purpose` |
| PLG | `biz-plg.md` | `general-purpose` |
| Flywheel | `biz-flywheel.md` | `general-purpose` |
| AI Monetization | `biz-ai-monetization.md` | `general-purpose` |

Read agent content via `Read(~/.claude/agents/[name].md)` before execution and inject into the prompt.

### Parallel Execution Template

```
Task(subagent_type="general-purpose", run_in_background=True,
  prompt="Analyze only from the [FrameworkA] expert perspective. Ignore other framework perspectives.

{problem}

### Key Findings (3+, with measurable metrics)
### Biggest Risk (1, with specific evidence)
### Immediately Actionable Prescription (something you can do today)")

Task(subagent_type="[AgentB]", run_in_background=True,
  prompt="Analyze only from the [FrameworkB] expert perspective. Ignore other framework perspectives.

{problem}

### Key Findings (3+, with measurable metrics)
### Biggest Risk (1, with specific evidence)
### Immediately Actionable Prescription (something you can do today)")

# If 3 selected, add:
Task(subagent_type="[AgentC]", run_in_background=True,
  prompt="Analyze only from the [FrameworkC] expert perspective. ...")
```

---

## Step 2: Synthesis — Delegate to biz-framework-integrator

After all agents complete, delegate synthesis to `biz-framework-integrator`:

```
Task(subagent_type="general-purpose",
  prompt="Integrate the following [N] framework expert analyses and output a final diagnosis.

Selected frameworks: [A] + [B] (+ [C])

=== [FrameworkA] Analysis ===
{result_A}

=== [FrameworkB] Analysis ===
{result_B}

(=== [FrameworkC] Analysis ===
{result_C})

Synthesis requirements:
1. Items flagged by 2+ agents simultaneously = cross blind spots → highest priority
2. If frameworks conflict, state the tradeoff explicitly
3. Top 3 action items must consist only of 'things you can do today'
4. Include 6-month pivot signals

Output format:
## Cross Blind Spots (flagged by multiple frameworks simultaneously)
## Framework Conflicts & Tradeoffs
## Verified Top 3 Action Items (as of today)
## 6-Month Pivot Signals")
```

---

## Output Format

```
### Selected Frameworks: [A] + [B] (+ [C])
### Selection Rationale: [Stage] / [Problem Type]

---
### Cross Blind Spots (flagged by multiple frameworks simultaneously)
...

### Framework Conflicts & Tradeoffs
[FrameworkA] vs [FrameworkB]: ...
→ Recommended resolution: ...

### Verified Top 3 Action Items
1. ...
2. ...
3. ...

### 6-Month Pivot Signals
- When [metric] is achieved → move to [next framework]
```

---

## Quality Check

Verify before synthesis:
- [ ] Do selected frameworks match the current stage priority table?
- [ ] Are cross blind spots explicitly stated?
- [ ] If frameworks conflict, are tradeoffs explained?
- [ ] Are Top 3 items executable today?

If any is No → re-run synthesis

---

## Quick Reference: Default Selections by Problem Type

| Problem Keywords | Default Selection |
|-----------------|------------------|
| "Growth stalled", "user churn" | AARRR + Growth Loop |
| "Not making money", "monetization" | AI Monetization + PLG |
| "Where to find customers" | GTM + BMC |
| "Competitors catching up", "moat" | Flywheel + Growth Loop |
| "Free→paid conversion not working" | PLG + AARRR |
| "Is the business model right" | BMC + AI Monetization |
| "Convincing investors" | Growth Loop + Flywheel |

---

## Documentation Obligation (MANDATORY)

After pipeline execution, **agent responses and final conclusions must be saved as a document**. Skipping documentation means the pipeline is considered **incomplete**.

### Saving Rules

1. **Save path**: `docs/research/[YYYYMMDD]-[topic-summary].md` (project docs folder)
2. **Save timing**: **Immediately before** returning the final answer to the user
3. **DOC_INDEX.md update**: Register in the `docs/DOC_INDEX.md` top table after saving
4. **Content to save**:

```markdown
# [bs-framework-synthesis] {Topic Summary}
**Date**: {YYYY-MM-DD}  **Skill**: bs-framework-synthesis

## Original Problem
{problem}

## Selected Frameworks
{[A] + [B] (+ [C])} — Selection rationale: {stage/problem type}

## Agent Response Summary
{Key findings + risks + prescriptions summary for each framework}

## Cross Blind Spots
{Items flagged by multiple frameworks simultaneously}

## Framework Conflicts & Tradeoffs
{Conflict items + recommended resolutions}

## Final Conclusion
{Verified Top 3 action items + 6-month pivot signals}
```
