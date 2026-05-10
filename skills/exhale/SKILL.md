---
name: exhale
description: Transform inhaled knowledge into actionable experiments, code changes, or design documents. Works with any /inhale output — HarnessOS digests, file analyses, URL summaries, or concept explorations.
---

<Purpose>
exhale is the action step that converts /inhale output into concrete artifacts:
experiments, code changes, design documents, or hypothesis tests.

```
/inhale (absorb anything) → /exhale (design + implement) → /evolve → /live
```

Works with all /inhale output types:
- HarnessOS research digest → experiment designs
- File analysis → improvement proposals / refactor plans
- URL summary → design docs or code changes
- Concept exploration → hypothesis or design artifact
</Purpose>

<Use_When>
- After running /inhale — to act on absorbed insights
- User says "evolve", "act on insights", "turn this into an experiment", "apply this research"
- When a specific insight needs to become a concrete experiment or code change
- When /live's Suggested Next Actions need execution
</Use_When>

<Do_Not_Use_When>
- No recent /inhale has been run and no insights exist in session
- User wants to manually implement something specific (use omc-autopilot)
</Do_Not_Use_When>

<Configuration>
Defaults:
- source: "latest"              (use most recent inhale output, any type)
- mode: "auto"                  (auto-detect best mode from source type)
- max_actions: 3                (max artifacts per run)
- auto_commit: false
- link_to_source: true
</Configuration>

<Steps>

## Step 1: Detect Inhale Source

Determine what /inhale produced. Check in order:

1. **Session context** — did /inhale just run in this session? Use that output directly.
2. **HarnessOS digest file** — `docs/research/digests/*.md` (most recent)
3. **Nothing found** → suggest running `/inhale` first, exit.

Identify the source type:
- `harness_digest` — has `## HarnessOS Relevant Items` section with reflect_type fields
- `file_analysis` — has `## What it does` / `## Structure` / `## Key Logic` sections
- `url_summary` — has `## Source` / `## Key Claims / Findings` sections
- `concept_exploration` — has `## In This Codebase` / `## Gap Analysis` sections

Report:
```
[EXHALE] Source: {source_type} — {title or filename or category}
[EXHALE] Actionable items found: {N}
```

## Step 2: Extract Actionable Items

Extract items based on source type:

### harness_digest
Parse `## HarnessOS Relevant Items`:
- Each item: title, URL, source, relevance score, reflect_type, summary
- Rank by: `relevance_score × type_weight × novelty_bonus`
  - type_weight: stuck_agent=1.5, hypothesis_validation=1.3, skill_selection=1.2, evaluation=1.1, general=1.0
  - novelty_bonus: 1.2 if not in previous digest, else 1.0

### file_analysis
Extract from `## Actionable Insights` and `## Suggested Next Actions`:
- Each suggestion becomes one candidate artifact
- Rank by impact (judgment — architectural changes > style fixes)

### url_summary
Extract from `## Key Claims / Findings` and `## Actionable Insights`:
- Each claim that has a concrete application becomes one candidate
- Rank by applicability to current codebase/project

### concept_exploration
Extract from `## Gap Analysis` and `## Suggested Next Actions`:
- Each gap or improvement becomes one candidate
- Rank by severity (missing feature > inefficiency > style)

Select top `max_actions` items.

## Step 3: Classify Evolution Mode per Item

Determine best mode for each item (user can override with `--mode`):

| Source type | Default mode | Output location |
|---|---|---|
| harness_digest / stuck_agent | experiment | `experiments/stuck_agent/{name}_design.md` |
| harness_digest / hypothesis_validation | hypothesis | `experiments/hypothesis_validation/{name}.md` |
| harness_digest / skill_selection | design | `docs/research/designs/{name}.md` |
| harness_digest / evaluation | code | modify relevant scoring/eval code |
| file_analysis | code or design | `docs/research/designs/{name}.md` or direct edit |
| url_summary | design | `docs/research/designs/{name}.md` |
| concept_exploration | hypothesis or code | depends on gap severity |

If mode = "auto": pick the mode that best fits the item.

## Step 4: Generate Evolution Artifacts

For each item, generate the appropriate artifact:

### Mode: "experiment"
```markdown
# {Experiment Name} Design

## Source
- **Origin**: {title or filename}
- **Absorbed via**: /inhale {source_type} ({date})
- **Relevance**: {score or impact level}

## Core Insight
{3-5 sentence summary of the key finding/idea}

## Application
### Hypothesis
> {Concrete testable hypothesis}

### Current State (Baseline)
{What exists now}

### Proposed Change (Treatment)
{What would change}

### Experiment Protocol
{Paired comparison / A-B test / before-after, metrics, success criteria}

### Implementation Plan
{File-level plan: which files to create/modify}

### Expected Outcome
{Quantitative or qualitative prediction}
```

### Mode: "code"
- Read the relevant existing code
- Apply the insight as a concrete modification
- PR-ready diff with comments linking to source

### Mode: "design"
```markdown
# {Design Name}

## Source
{origin + date}

## Problem / Gap
{what issue this addresses}

## Proposed Design
{architecture or approach description}

## Integration Points
{where this connects to existing code/skills}

## Trade-offs
{what you gain vs what you give up}
```

### Mode: "hypothesis"
```markdown
# {Hypothesis Name}

## Source
{origin + date}

## Formal Statement
- H0: {null hypothesis}
- H1: {alternative hypothesis}

## Variables
- Independent: {what you change}
- Dependent: {what you measure}
- Controlled: {what you hold constant}

## Measurement Method
{how to measure}

## Success Criteria
{what counts as H1 supported}
```

## Step 4.5: Verification Gate (Evidence-Based Acceptance)

Every evolved artifact starts with status `proposed`. Only artifacts that pass
verification are promoted to `accepted`. This prevents unvalidated ideas from
polluting the project's knowledge base.

### Verification Status Lifecycle
```
proposed → [run experiment/test] → verified_positive → accepted
                                 → verified_negative → rejected (archived)
                                 → verified_neutral  → parked (revisit later)
         → [no experiment run]  → proposed (stays in queue)
```

### Verification Methods (by mode)

| Mode | Verification | Acceptance Criteria |
|---|---|---|
| experiment | Run the experiment design via omc-autopilot | p-value < 0.05 OR effect_size > threshold |
| code | Run tests (pytest/npm test) after applying change | All tests pass + no regression |
| design | Peer review via review-harsh-critic agent | No critical flaws identified |
| hypothesis | Run hypothesis test with real data | H1 supported at significance level |

### Verification Gate Protocol
```
for each artifact in evolved_artifacts:
    artifact.status = "proposed"
    artifact.verification_method = determine_method(artifact.mode)

    # Auto-verify if test infrastructure exists
    if artifact.mode == "code" AND project_has_tests():
        result = run_tests()
        if result.all_passed:
            artifact.status = "verified_positive"
        else:
            artifact.status = "verified_negative"
            artifact.rejection_reason = result.failures

    # For experiment/hypothesis: mark as proposed, queue for execution
    elif artifact.mode in ["experiment", "hypothesis"]:
        artifact.status = "proposed"
        artifact.next_action = "Run via /live or /live-inf to validate"

    # For design: auto-review if review agent available
    elif artifact.mode == "design":
        artifact.status = "proposed"
        artifact.next_action = "Review via review-harsh-critic"

# Track in verification registry
append_to(".omc/evolution-registry.jsonl", {
    "date": ISO8601,
    "source_paper": artifact.source_url,
    "artifact_path": artifact.path,
    "mode": artifact.mode,
    "status": artifact.status,
    "verification_method": artifact.verification_method,
    "verification_result": artifact.verification_result or null
})
```

### Acceptance Rules
- Only `accepted` artifacts inform future /inhale scoring (feedback loop)
- `rejected` artifacts are archived with reason — prevents re-evolution of failed ideas
- `proposed` artifacts queue up for the next /live or /live-inf execution
- An artifact stays `proposed` for max 7 days, then auto-archives as `expired`

### Registry File (.omc/evolution-registry.jsonl)
```json
{"date": "2026-04-03", "source_paper": "arXiv:2604.00356", "artifact_path": "experiments/stuck_agent/trajectory_triage_design.md", "mode": "experiment", "status": "proposed", "verification_method": "paired_comparison"}
{"date": "2026-04-03", "source_paper": "arXiv:2604.00478", "artifact_path": "experiments/stuck_agent/anti_sycophancy_gate_design.md", "mode": "experiment", "status": "verified_positive", "verification_result": {"effect_size": 0.08, "p_value": 0.03}}
```

## Step 5: Cross-Reference with Active Goals

Read `.omc/goal-tree.json`:
- If an evolution artifact directly serves the current `root_goal`, highlight it
- If it conflicts with current goals, flag the conflict

## Step 6: Present Results

Output summary:
```
[EVOLVE — {date}]
Evolved {N} insights from /inhale digest ({category})

1. {item_title} → {mode}: {artifact_path}
   Source: {source_name} ({url})

2. {item_title} → {mode}: {artifact_path}
   Source: {source_name} ({url})

3. {item_title} → {mode}: {artifact_path}
   Source: {source_name} ({url})

Knowledge loop: /inhale → /exhale complete.
Next: implement experiments, or /inhale again for fresh knowledge.
```

</Steps>

<Examples>

## After HarnessOS research inhale
```
User: /inhale agent_research
User: /exhale
→ Reads latest HarnessOS digest
→ Selects top 3 items by evolution_score
→ Generates experiment designs
```

## After file inhale
```
User: /inhale stop-playwright-detect.sh
User: /exhale
→ Uses session file_analysis output
→ Extracts Actionable Insights + Suggested Next Actions
→ Generates code or design artifacts
```

## After URL inhale
```
User: /inhale https://example.com/paper
User: /exhale --mode hypothesis
→ Uses session url_summary output
→ Generates testable hypothesis from key claims
```

## After concept inhale
```
User: /inhale has_uncommitted_targets
User: /exhale
→ Uses session concept_exploration output
→ Gap analysis → design or code artifact
```

</Examples>

<Integration>
## Knowledge Evolution Loop

```
/inhale ─── collect + filter + inject ───► session context + digest
    │
    └──► /exhale ─── analyze + design + implement ───► artifacts
              │
              ├── experiments/stuck_agent/*.md
              ├── experiments/hypothesis_validation/*.md
              ├── docs/research/designs/*.md
              └── code changes (PR-ready)
                     │
                     └──► /live ─── execute experiments ───► results
                                │
                                └──► /inhale (next cycle — informed by results)
```

| Skill | Relationship |
|---|---|
| /inhale | Upstream — provides the knowledge to evolve |
| /live | Downstream — executes the evolved artifacts |
| /omc-autopilot | Can execute individual evolved code changes |
| /entity | Meta-skill that can orchestrate inhale → evolve → live |
| experiments/* | Target directories for experiment artifacts |
</Integration>
