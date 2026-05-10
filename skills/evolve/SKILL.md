---
name: evolve
description: Knowledge evolution pipeline orchestrator — inhale→exhale→live full loop with smart state detection. Bridges exhale artifact_path to live root_goal format. Executes one proposed artifact at a time (Goodhart protection). Use when knowledge absorption should translate to running experiments.
---

<Purpose>
evolve is the pipeline glue that closes the knowledge evolution loop:

```
/inhale  (collect)   → digest file
/exhale  (design)    → evolution-registry.jsonl (proposed artifacts)
/evolve  (transform) → converts artifact_path → root_goal, routes to /live
/live    (execute)   → verified results → registry feedback
```

Two structural gaps currently break the loop:
1. inhale → exhale: no trigger (manual invocation needed)
2. exhale → live: format mismatch (artifact_path ≠ root_goal string)

evolve fixes both. It is NOT an automation-for-automation's-sake glue.
It is a stateful state router + format transformer that runs ONE item at a time.
</Purpose>

<Use_When>
- After /inhale or /exhale — to continue the loop toward execution
- User says "evolve", "run the pipeline", "execute pending experiments", "close the loop"
- When evolution-registry.jsonl has proposed items that haven't been executed
- Periodic execution: "evolve the latest knowledge"
- `/evolve "entity 개선"` — direct-goal mode: bypasses registry, runs live-inf with goal directly
</Use_When>

<Do_Not_Use_When>
- User wants to run all 9 pending artifacts at once — warn and suggest max_items=1 default
- No digest and no proposed items exist AND no direct goal given — suggest /inhale first
</Do_Not_Use_When>

<Configuration>
Defaults:
- max_items: 1             (execute one artifact per evolve run — Goodhart protection)
- skip_inhale: false       (run /inhale unless fresh digest exists < 24h)
- skip_exhale: false       (run /exhale unless proposed items already exist)
- priority_mode: "score"   (select artifact by evolution_score; alt: "oldest", "newest", "mode:experiment")
- category: "agent_research" (inhale category if inhale runs)
- auto_verify: true        (attempt verification after live execution)
</Configuration>

<Steps>

## Args Parsing (FIRST — before any other step)

```
args = invocation arguments (everything after /evolve)
args_stripped = args.strip()

if args_stripped and not args_stripped.startswith("--"):
    # DIRECT-GOAL MODE: bypass registry entirely
    goal = args_stripped
    emit: "[EVOLVE] Direct-goal mode — registry bypassed"
    emit: "[EVOLVE] Goal: {goal}"
    → Skill('live-inf', args=goal)
    → STOP
else:
    # REGISTRY MODE: existing behavior (Steps 1-8 below)
    # --flags like --skip-inhale, --skip-exhale, etc. still parsed in their respective steps
    proceed with Steps 1-8
```

Examples:
```
/evolve                           → REGISTRY MODE (no args)
/evolve entity 개선                 → DIRECT-GOAL MODE → live-inf "entity 개선"
/evolve "stuck agent experiment"  → DIRECT-GOAL MODE → live-inf "stuck agent experiment"
/evolve --skip-inhale             → REGISTRY MODE (flag only)
/evolve --priority-mode oldest    → REGISTRY MODE (flag only)
```

---

## Step 1: State Detection

Read the current pipeline state to determine entry point:

```bash
# Check evolution-registry for pending items
cat .omc/evolution-registry.jsonl | python3 -c "
import sys, json
items = [json.loads(l) for l in sys.stdin]
proposed = [x for x in items if x['status'] == 'proposed']
print(f'proposed: {len(proposed)}')
print(f'accepted: {len([x for x in items if x[\"status\"] == \"accepted\"])}')
"

# Check latest digest age
ls -t docs/research/digests/*.md 2>/dev/null | head -1
```

Routing table:
| Condition | Action |
|-----------|--------|
| proposed items exist | SKIP inhale + exhale → go to Step 4 (priority select) |
| fresh digest exists (< 24h) AND no proposed | SKIP inhale → go to Step 3 (exhale) |
| no digest OR digest > 24h AND no proposed | run full pipeline: Step 2 → 3 → 4 → 5 |
| `--skip-inhale` flag | force skip Step 2 |
| `--skip-exhale` flag | force skip Step 3 |

Report state:
```
[EVOLVE] State: {N} proposed | {M} accepted | digest: {age or "none"}
[EVOLVE] Entry point: {RESUME | EXHALE_ONLY | FULL}
```

## Step 2: Inhale (conditional)

Skip if: proposed items exist OR fresh digest (< 24h) OR `--skip-inhale`.

```
Skill('inhale', args='{category}')
```

After inhale: proceed to Step 3.

## Step 3: Exhale (conditional)

Skip if: proposed items already exist in registry OR `--skip-exhale`.

```
Skill('exhale', args='')
```

After exhale: proceed to Step 4.

## Step 4: Priority Selection

Select ONE artifact from proposed items (max_items=1 default):

### Priority Scoring

```python
# Read evolution-registry.jsonl
proposed = [x for x in registry if x['status'] == 'proposed']

# Mode weights (higher = higher priority)
mode_weight = {
    'experiment':  1.5,   # directly executable by /live
    'hypothesis':  1.3,   # testable hypothesis
    'code':        1.2,   # concrete implementation
    'design':      0.8,   # needs review before execution
}

# Age score: older = lower (avoid stale items)
from datetime import date, datetime
today = date.today()
for item in proposed:
    age_days = (today - datetime.strptime(item['date'], '%Y-%m-%d').date()).days
    if age_days > 7:
        age_penalty = 0.7
    else:
        age_penalty = 1.0

    item['_priority'] = mode_weight.get(item['mode'], 1.0) * age_penalty

selected = max(proposed, key=lambda x: x['_priority'])
```

If `priority_mode` = "oldest": select oldest proposed item.
If `priority_mode` = "mode:experiment": filter to experiment mode first.

Report:
```
[EVOLVE] Selected: {artifact_path}
         Source: {source_paper}
         Mode: {mode} | Verification: {verification_method}
         Priority score: {_priority:.2f}
```

## Step 5: Format Transformation (exhale → live)

**This is the core transformation** — convert artifact file into live-compatible root_goal.

```bash
# Read the artifact file
cat {selected.artifact_path}
```

Extract goal from artifact:
- If mode = "experiment": read `## Hypothesis` section → use as root_goal
- If mode = "hypothesis": read `## Formal Hypothesis` or H1 statement
- If mode = "code": read first `### Implementation Plan` or objective line
- If mode = "design": read first paragraph under `## HarnessOS Application`

Construct root_goal string:
```
root_goal = "[{mode.upper()}] {hypothesis_or_objective}"

# Example:
# "[EXPERIMENT] Testing whether trajectory triage reduces stuck-agent rate
#  vs baseline (current linear retry) — paired comparison, target effect_size > 0.1"
```

Update goal-tree.json:
```bash
python3 -c "
import json
with open('.omc/goal-tree.json', 'r') as f:
    tree = json.load(f)
tree['root_goal'] = '{root_goal}'
tree['original_goal'] = '{root_goal}'
tree['_evolve_source'] = '{selected.artifact_path}'
tree['_evolve_source_paper'] = '{selected.source_paper}'
tree['evolution_count'] = 0
tree['evolution_history'] = []
with open('.omc/goal-tree.json', 'w') as f:
    json.dump(tree, f, indent=2)
print('goal-tree.json updated')
"
```

Report:
```
[EVOLVE] goal-tree.json ← "{root_goal[:80]}..."
[EVOLVE] Source artifact: {artifact_path}
```

## Step 6: Live Execution

Hand off to /live:

```
Skill('live', args='Goal: {root_goal}')
```

/live handles: scoring, evolution, convergence, episode memory.

## Step 7: Registry Feedback (post-live)

After /live completes, update registry status:

```python
# Read /live result (from live-state.json)
with open('.omc/live-state.json') as f:
    state = json.load(f)

verdict = state.get('last_outcome', 'unknown')
best_score = state.get('best_score', 0.0)

# Map live outcome to registry status
status_map = {
    'success':            'verified_positive',
    'CONVERGED_SUCCESS':  'verified_positive',
    'CONVERGED_STALE':    'verified_neutral',
    'fatal_escalation':   'verified_negative',
    'exhausted':          'verified_neutral',
}
new_status = status_map.get(verdict, 'verified_neutral')

# Update registry entry
lines = open('.omc/evolution-registry.jsonl').readlines()
updated = []
for line in lines:
    entry = json.loads(line)
    if entry['artifact_path'] == selected['artifact_path'] and entry['status'] == 'proposed':
        entry['status'] = new_status
        entry['verification_result'] = {
            'outcome': verdict,
            'best_score': best_score,
            'executed_at': ISO8601_now()
        }
        if new_status == 'verified_positive':
            entry['status'] = 'accepted'
    updated.append(json.dumps(entry, ensure_ascii=False))

open('.omc/evolution-registry.jsonl', 'w').write('\n'.join(updated) + '\n')
```

## Step 8: Summary

```
[EVOLVE — {date}]
Pipeline: {FULL | EXHALE_ONLY | RESUME}

Executed: {artifact_path}
Goal: "{root_goal[:80]}..."
Outcome: {verdict} | Score: {best_score:.2f}
Registry: proposed → {new_status}

Remaining proposed: {N-1} items
Next: run /evolve again OR /inhale for fresh knowledge
```

</Steps>

<CLI>

## Usage

```bash
/evolve                           # smart routing, execute 1 item
/evolve --skip-inhale             # skip inhale, use existing digest
/evolve --skip-exhale             # skip inhale+exhale, execute pending items
/evolve --max-items 3             # execute up to 3 items (CAUTION: Goodhart risk)
/evolve --priority-mode oldest    # execute oldest proposed item first
/evolve --priority-mode mode:experiment  # prioritize experiment-mode items
/evolve agent_research            # full pipeline with specific inhale category
```

## Typical Loop

```bash
/inhale agent_research            # absorb latest research
/exhale                           # design artifacts from digest
/evolve --skip-inhale --skip-exhale  # execute top-priority artifact
# → /live runs, scores, converges
# → registry updated: proposed → accepted
/evolve --skip-inhale --skip-exhale  # execute next item
```

Or just:
```bash
/evolve                           # handles all of the above automatically
```

</CLI>

<Integration>

## Pipeline Position

```
/inhale ──→ digest ──→ /exhale ──→ evolution-registry (proposed)
                                         │
                                    /evolve (this skill)
                                         │ format transform
                                         ↓
                               goal-tree.json (root_goal)
                                         │
                                      /live
                                         │
                                    verified result
                                         │
                               evolution-registry (accepted/rejected)
                                         │
                               /inhale (next cycle — feedback-informed)
```

| Skill | Relationship |
|-------|-------------|
| /inhale | Upstream — provides digests; evolve calls it conditionally |
| /exhale | Upstream — provides proposed artifacts; evolve calls it conditionally |
| /live | Downstream — executes goals; evolve hands off to it |
| /entity | Meta-harness — can wrap evolve: `/entity-live "close the knowledge loop"` |

</Integration>
