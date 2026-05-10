# Skill Interface: live-inf
# Version: 1.0.0
# Last updated: 2026-04-09

## Input Contract

```yaml
optional:
  goal:
    type: string
    description: "Task to pursue. If omitted, resumes from .omc/infinite-state.json"
    format: "Goal: <description>" or plain string
    max_length: 10000
  flags:
    type: string
    description: "Parsed from args prefix: -i/--inf (routes to live-inf from /live)"
```

## Resume Behavior
- If `.omc/infinite-state.json` exists with `status=ROTATING`: auto-resume (no input needed)
- If exists with `status=CONVERGED|USER_STOPPED`: ignore, start fresh with provided goal
- If no goal + no resumable state: error `NO_ACTIVE_GOAL`

## Output Contract

```yaml
# live-inf runs until convergence — output is delivered incrementally via log messages.
# Final output on termination:

converged_success:
  status: CONVERGED_SUCCESS
  total_iterations: integer
  total_sessions: integer
  best_score: float   # 0.0–1.0
  final_goal: string
  score_trajectory: array[float]
  evolution_history:
    type: array
    items:
      goal: string
      score: float
      iteration: integer

converged_stale:
  status: CONVERGED_STALE
  best_score: float
  min_required: float  # 0.6 default
  rollback_commands: array[string]  # git commands to restore best iteration

user_stopped:
  status: USER_STOPPED
  iterations_completed: integer
  best_score: float

escalated:
  status: ESCALATED  # dead_ends >= max_dead_ends
  dead_end_count: integer
  world_model_summary: string
  # Awaits user: new direction or adjusted goal

error:
  status: ERROR
  code: enum [NO_ACTIVE_GOAL, DIRTY_STATE, CONTEXT_ROTATION_FAILED]
  message: string
```

## Idempotency
- **NOT idempotent**: each iteration mutates project state.
- **Resume-safe**: re-running after interruption resumes from last checkpoint.
- Checkpoint: `git log --oneline | grep "live-inf iter"` shows all rollback points.

## Side Effects
- Repeatedly invokes `omc-autopilot` (or delegates to ORCHESTRATOR_MAP skills)
- Writes: `.omc/infinite-state.json`, `.omc/world-model.json`, `.omc/live-state.json`
- Appends: `.omc/episodes.jsonl`, `.omc/live-progress.log`
- Creates git commits every iteration (checkpoint commits)
- Emergency context rotation writes `.omc/infinite-state.json` status=ROTATING

## Stop Signal (user-side)
```bash
echo "stop" > .omc/infinite-stop.txt   # graceful stop after current iteration
```

## Dependencies
- Requires: `omc-autopilot` (or task-type-specific orchestrator)
- Requires: `omc-episode-memory`, `omc-goal-tree`
- Optional: any skill available in system-reminder skills list (for Wave 1 + Skill Router)

## Handoff To (inter-session)
| Mechanism | When | Data |
|-----------|------|------|
| `.omc/infinite-state.json` | On context rotation or interruption | Full session state |
| `.omc/world-model.json` | Every iteration | Epistemic state (tried strategies, dead ends, HER hints) |
| `.omc/episodes.jsonl` | On convergence or partial | Execution episode summary |

## Version Compatibility
- v1.0.0: Initial formal interface definition
- Inherits: `live` v1.0.0 interface for all inner-loop mechanics
