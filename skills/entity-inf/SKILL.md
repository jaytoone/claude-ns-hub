---
name: entity-inf
description: "Standalone infinite corpus evolution loop for Entity domains. Explorer-Reasoner-Auditor swarm with 4D Corpus Quality Oracle, context rotation, world model. omc-independent. Converges only when all 4 quality dimensions plateau."
---

# /entity-inf — Infinite Corpus Evolution Loop

**Architecture**: Standalone infinite swarm loop — NOT a /live-inf wrapper.
Inherits entity-live swarm cycle (Explorer→Reasoner→Auditor) with infinite-mode additions:
context rotation, world model persistence, novelty escape, stricter convergence.

```
entity-inf (Infinite Corpus Evolution Loop)
  ├── [STIGMERGY]  Corpus State — docs as pheromone trails
  ├── [SWARM]      Explorer (parallel) + Reasoner (sequential) + Auditor (parallel)
  ├── [4D ORACLE]  grounding_rate + routing_precision + claim_quality + sycophancy_pass
  ├── [EVOLVE]     Gap-driven goal elevation (weakest dimension + weakest doc)
  ├── [RESEARCH]   Auto-triggered expert-research on corpus gaps
  ├── [ROTATE]     Context Rotation — .entity/infinite-state.json
  └── [WORLD MODEL] Epistemic State — tried, dead ends, pheromone, research cache
```

## Relationship to entity-live

entity-inf IS entity-live with 4 overrides:
1. max_iterations: null (no budget ceiling — convergence only)
2. plateau_k: 5 (stricter — 5 consecutive all-dim stagnant)
3. Context Rotation added (auto-resume across sessions)
4. Novelty Escape added (attempt novel goal before declaring convergence)

All entity-live steps (Explorer, Reasoner, Auditor, 4D Oracle, stigmergy) are inherited unchanged.

## Activation

```
/entity-inf [question]     ← infinite loop (convergence only)
```

## Configuration Overrides (from entity-live)

```yaml
max_iterations: null           # infinite — convergence/user-stop only
plateau_k: 5                   # 5 consecutive all-dim stagnant → converge
epsilon: 0.03                  # inherited
quality_threshold: 0.70        # inherited (MAE 0.7 gate)
exploration_rate: 0.15         # inherited
max_escape_attempts: 2         # novelty escape before true convergence
max_dead_ends: 10              # escalate to user after 10 dead-end strategies
context_budget_pct: 90         # emergency rotation (auto-compact handles normal)
state_dir: ".entity"            # shared with entity-live
```

## Protocol

### PRE-LOOP: Initialize or Resume

**Step 0a — Resume Check (extended for context rotation):**
```python
if .entity/infinite-state.json exists:
    inf_state = read(".entity/infinite-state.json")
    if inf_state.status == "ROTATING":
        # Previous session hit context limit — seamless resume
        restore_all_state(inf_state)
        emit: "[RESUME] Session {inf_state.session_id} | iter {inf_state.iteration} | best={inf_state.best_score:.2f}"
        → skip init, go to Step 0c (World Model)
    elif inf_state.status in ["CONVERGED", "USER_STOPPED"]:
        → fresh start

# ESC recovery: check for dirty state
if git has uncommitted changes AND live-state.last_outcome is null:
    emit: "[WARN] Dirty state from interrupted session. Stash/commit/continue?"
    → wait for user input

# Fresh start (same as entity-live Step 0b)
if question is empty:
    → error: "No active goal. Run /entity-inf <question> to start."
```

Steps 0b, 0c, 0d: **Identical to entity-live** (state init, world model load, stigmergy init).

### MAIN LOOP (infinite — convergence only)

**Steps 1-4: Identical to entity-live** (Explorer → Reasoner → Auditor → 4D Oracle).

**Step 5: CONVERGENCE CHECK — Extended:**
```python
convergence_status, details = check_convergence(
    quality_history, plateau_k=5, epsilon=0.03, quality_threshold=0.70
)

# User stop signal
if .entity/stop.txt exists:
    → USER_STOPPED (graceful shutdown)
```

**Step 6: Decision Branch — Extended with Novelty Escape:**
```python
if convergence_status == "CONVERGED":
    # NOVELTY ESCAPE before declaring true convergence
    if escape_attempts < max_escape_attempts:
        emit: "[NOVELTY ESCAPE] Attempt {escape_attempts+1}/{max_escape_attempts}"

        # Generate maximally different goal from all tried strategies
        escape_goal = generate_novel_goal(
            original_goal=state.original_goal,
            tried=world_model.tried,
            pheromone=world_model.pheromone,
            quality_vector=qv
        )
        state.root_goal = escape_goal
        state.plateau_count = 0
        escape_attempts += 1
        → continue to Step 7 → next iteration

    else:
        # True convergence — escape exhausted
        if qv["total"] >= quality_threshold:
            → CONVERGED_SUCCESS
        else:
            → CONVERGED_STALE

elif convergence_status in ["IMPROVE", "EVOLVE", "CONTINUE"]:
    # Same as entity-live Step 6
    ...
```

**Step 7: State Update — Extended with context check:**
```python
# Steps 7a-7g: Identical to entity-live

# 7h — Context Rotation Check (replaces budget check)
# Auto-compact handles normal context growth.
# Only rotate at 90% as emergency fallback.
estimated_context_pct = estimate_context_usage()

if estimated_context_pct >= 90:
    inf_state = {
        "status": "ROTATING",
        "session_id": f"inf-{timestamp}",
        "iteration": state.iteration,
        "root_goal": state.root_goal,
        "original_goal": state.original_goal,
        "evolution_count": state.evolution_count,
        "best_score": state.best_score,
        "best_score_vector": state.best_score_vector,
        "plateau_count": state.plateau_count,
        "quality_history": state.quality_history[-10:],  # last 10 only
        "escape_attempts": escape_attempts,
        "rotated_at": ISO8601_now()
    }
    write(".entity/infinite-state.json", inf_state)
    emit: """
    [CONTEXT ROTATION] ~{estimated_context_pct:.0f}%
    Session {inf_state.session_id} | Iter {state.iteration} | Best: {state.best_score:.2f}
    TO RESUME: run /entity-inf in a new session
    """
    → STOP

# 7i — Dead end escalation
if len(world_model.dead_ends) >= max_dead_ends:
    emit: "[ESCALATE] {max_dead_ends} dead-end strategies reached. Need new direction."
    → wait for user input (new goal or stop)

# No budget check — infinite mode loops until convergence
→ next iteration
```

### POST-LOOP: Termination

**CONVERGED_SUCCESS / CONVERGED_STALE / USER_STOPPED:**
Same as entity-live, plus:
```python
inf_state.status = "CONVERGED"  # or "USER_STOPPED"
inf_state.final_score = state.best_score
inf_state.total_iterations = state.iteration
write(".entity/infinite-state.json", inf_state)
```

### Novelty Escape Protocol

```python
def generate_novel_goal(original_goal, tried, pheromone, quality_vector):
    """Generate a goal maximally different from all tried strategies."""
    DIMS = ["grounding_rate", "routing_precision", "claim_quality", "sycophancy_pass"]

    # Find least-explored dimension
    explored = {d: max((t["score_vector"].get(d, 0) for t in tried), default=0) for d in DIMS}
    least_explored = min(explored, key=explored.get)

    # Find least-touched doc
    least_touched = min(pheromone.items(), key=lambda x: x[1]["strength"])

    # Build escape goal targeting neglected areas
    return f"Novel approach: improve {least_explored} via {least_touched[0]} " \
           f"using a method NOT in: {[t['goal'][:30] for t in tried[-5:]]}. " \
           f"Original context: {original_goal}"
```

## State Files

```
.entity/
  live-state.json         # shared with entity-live (iteration, quality history)
  infinite-state.json     # context rotation bridge (session continuity)
  world-model.json        # epistemic state (shared with entity-live)
  progress.log            # per-iteration JSONL (shared with entity-live)
  stop.txt                # create this file to signal graceful stop
```

**User stop signal:**
```bash
echo "stop" > .entity/stop.txt
```

## Anti-patterns

- Same as entity-live, plus:
- Do NOT ask user mid-loop — fully autonomous until convergence or stop signal
- Do NOT declare convergence until plateau_k=5 consecutive stagnant iterations
- Do NOT skip Novelty Escape — always attempt before true convergence
