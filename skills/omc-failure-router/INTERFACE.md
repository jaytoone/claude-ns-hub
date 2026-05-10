# Skill Interface: omc-failure-router
# Version: 1.0.0
# Last updated: 2026-04-09

## Input Contract

```yaml
required:
  error_context:
    type: object
    fields:
      error_message:
        type: string
        description: "Raw error message (will be normalized: strip line numbers, addresses)"
      phase:
        type: enum
        values: [expansion, planning, execution, qa, validation, unknown]
        description: "Phase in which the error occurred"
      occurrence_count:
        type: integer
        description: "How many times this error pattern has been seen in this run (1-based)"
        min: 1
      prior_reflexion:
        type: string
        description: "Reflexion from previous Type 2 attempt, if any"
        nullable: true
      goal_context:
        type: string
        description: "Current goal text — used for Fatal escalation messages"
        max_length: 500
```

## Output Contract

```yaml
classification:
  type: enum
  values: [transient, persistent, fatal, exogenous]

transient:
  classification: transient
  action: retry
  max_retries: 3
  backoff_seconds: 0  # immediate retry unless exogenous

persistent:
  classification: persistent
  action: restructure
  reflexion:
    type: string
    description: "Generated reflexion: WHY failed, WHAT assumption wrong, WHAT try next, HOW verify"
    nullable: false  # always present for persistent; may say "REFLEXION_FAILED: [reason]" if LLM call failed
  restructuring_suggestions:
    type: array
    items: string
  next_strategy: string

fatal:
  classification: fatal
  action: escalate
  goal_update_required: true
  handoff_report: string
  episode_save_required: true

exogenous:
  classification: exogenous
  error_type: enum [http_5xx, timeout, permission, disk, network, rate_limit]
  action: enum [retry_with_backoff, skip, escalate_to_user]
  wait_seconds: integer  # backoff duration

error:
  classification: error
  code: enum [REFLEXION_GENERATION_FAILED, HISTORY_FILE_CORRUPT, INPUT_VALIDATION_FAILED]
  message: string
  fallback_classification: enum [transient, persistent]  # safe default to use
```

## Idempotency
- **Idempotent for classification**: same inputs → same classification.
- **NOT idempotent for reflexion**: each call generates a new LLM reflexion (may vary).
- **Side effect**: appends to `.omc/failure-history.json`

## Side Effects
- Reads and writes `.omc/failure-history.json`
- Does NOT write episodes (caller's responsibility on fatal)
- Does NOT update goal-tree (caller's responsibility on fatal)

## Failure Recovery
- If LLM reflexion call itself fails: return `classification: persistent` with `reflexion: "REFLEXION_FAILED: [error]"` and fallback suggestions — never block the pipeline.
- If `.omc/failure-history.json` is corrupt: log warning, rebuild from scratch (empty history), continue.

## Dependencies
- Requires: write access to `.omc/failure-history.json`
- Requires: LLM access (for persistent reflexion generation)

## Downstream Consumers
- `omc-autopilot` (Phase 3): primary caller on QA cycle failure
- `live` / `live-inf` (NOT YET branch): may classify autopilot-level failures

## Handoff To
| Downstream | Condition | Data Passed |
|-----------|-----------|-------------|
| `omc-goal-tree` | fatal classification | goal_update_required=true + handoff_report |
| `omc-episode-memory` | fatal classification | caller must invoke with outcome=failure |

## Version Compatibility
- v1.0.0: Initial formal interface definition
