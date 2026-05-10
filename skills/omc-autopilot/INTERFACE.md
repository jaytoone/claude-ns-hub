# Skill Interface: omc-autopilot
# Version: 1.0.0
# Last updated: 2026-04-09

## Input Contract

```yaml
required:
  task:
    type: string
    description: "Product idea or task description (2-3 lines minimum; must include domain + key features)"
    min_length: 20
    max_length: 5000

optional:
  skip_phases:
    type: array
    items: enum [expansion, planning]
    description: "Phases to skip (auto-detected if ralplan/deep-interview spec exists)"
  phase_start:
    type: enum
    values: [expansion, planning, execution, qa, validation]
    default: expansion
    description: "Override phase detection and start from this phase"
  config_override:
    type: object
    description: "Override settings.json omc.autopilot values for this run"
    fields:
      maxQaCycles: integer (default: 5)
      maxValidationRounds: integer (default: 3)
      skipQa: boolean (default: false)
      skipValidation: boolean (default: false)
```

## Output Contract

```yaml
success:
  phase_reached:
    type: string
    description: "Last phase completed (expansion|planning|execution|qa|validation|cleanup)"
  artifacts:
    type: array
    description: "Files created or modified during execution"
    items:
      type: object
      fields:
        path: string
        operation: enum [created, modified, deleted]
  qa_result:
    type: object
    fields:
      cycles_used: integer
      tests_passed: boolean
      build_succeeded: boolean
  validation_result:
    type: object
    fields:
      rounds_used: integer
      architect_approved: boolean
      security_approved: boolean
      code_reviewer_approved: boolean
      da_triggered: boolean  # true if anti-sycophancy gate fired
  episode_saved: boolean

failure:
  phase_failed:
    type: enum
    values: [expansion, planning, execution, qa, validation, cleanup]
  failure_type:
    type: enum
    values: [transient, persistent, fatal]
    description: "Classification from omc-failure-router"
  error_pattern: string
  handoff_report_path: string  # written on fatal failure
  qa_cycles_exhausted: boolean
  validation_rounds_exhausted: boolean
```

## Idempotency
- **NOT idempotent**: execution mutates project files.
- Safe to resume (re-run after failure restores from state file).
- State file: `.omc/state/autopilot-state.json` — contains `phase`, `qa_cycle_count`, `validation_round`.

## Side Effects
- Writes/modifies project source files
- Writes `.omc/state/autopilot-state.json` (cleared on success)
- Writes `.omc/episodes.jsonl` (episode memory on completion)
- Writes `.omc/autopilot/spec.md` (Phase 0 output)
- Writes `.omc/plans/autopilot-impl.md` (Phase 1 output)
- May invoke `omc-failure-router`, `omc-goal-tree`, `omc-episode-memory`

## Dependencies
- Requires: `omc-failure-router` (Phase 3 failure classification)
- Requires: `omc-episode-memory` (Phase 5 save)
- Requires: `omc-goal-tree` (Phase 3 fatal escalation)
- Requires: `review-harsh-critic` (Phase 4 anti-sycophancy gate)
- Optional: `omc-plan` / `omc-deep-interview` (Phase 0/1 skip detection)

## Downstream Consumers
- `live` / `live-inf`: primary inner loop executor for `task_type=code|debug|ui`
- `omc-goal-tree`: receives fatal failure escalation
- `omc-episode-memory`: receives completion summary

## Handoff To
| Downstream Skill | Condition | Data Passed |
|-----------------|-----------|-------------|
| `omc-failure-router` | QA cycle repeats same error 3x | error_pattern, phase context |
| `omc-goal-tree` | fatal failure | failure summary + original goal |
| `omc-episode-memory` | phase 5 completion | full execution summary |

## Version Compatibility
- v1.0.0: Initial formal interface definition
- Breaking change policy: increment major version; old callers continue on v(N-1) shim
