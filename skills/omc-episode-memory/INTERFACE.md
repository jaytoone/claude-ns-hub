# Skill Interface: omc-episode-memory
# Version: 1.0.0
# Last updated: 2026-04-09

## Input Contract

```yaml
required:
  mode:
    type: enum
    values: [save, load]

# SAVE mode fields:
save:
  required:
    outcome:
      type: enum
      values: [success, failure, partial]
    task_desc:
      type: string
      description: "What the agent was trying to do"
      max_length: 500
    phase_reached:
      type: string
      description: "Last phase completed (e.g. 'phase_4', 'phase_3_qa_cycle_2')"
  optional:
    high_quality:
      type: boolean
      default: false
      description: "Mark as GOLD episode (success + all tests passed + no known regressions)"
    key_errors:
      type: array
      items: string
      description: "Error messages encountered (normalized: strip line numbers)"
    key_decisions:
      type: array
      items: string
      description: "Important choices made during the run"
    failure_patterns:
      type: array
      description: "Tier 2/3 failure patterns from omc-failure-router (stored only if count >= 2)"
      items:
        type: object
        fields:
          pattern: string
          count: integer
          generalizable: boolean
    related_episodes:
      type: array
      items: string
      description: "IDs of past episodes in same problem domain (Zettelkasten linking)"
    tags:
      type: array
      items: string

# LOAD mode fields:
load:
  optional:
    query:
      type: string
      description: "Current goal text — used for TF-IDF relevance scoring"
      default: ""
    top_k:
      type: integer
      default: 3
      description: "Number of relevant episodes to return"
    min_quality:
      type: float
      default: 0.6
      description: "Minimum quality score (0.0-1.0)"
    max_age_iterations:
      type: integer
      description: "Exclude episodes older than N iterations (null = no limit)"
      nullable: true
    exclude_outcome:
      type: array
      items: enum [success, failure, partial]
      description: "Filter out episodes with these outcomes"
```

## Output Contract

```yaml
# SAVE mode:
save_success:
  episode_id: string  # sha256(ts + task_desc)[:16]
  saved_to: ".omc/episodes.jsonl"
  high_quality: boolean

save_error:
  code: enum [WRITE_FAILED, DUPLICATE_DETECTED]
  message: string

# LOAD mode:
load_success:
  episodes:
    type: array
    items:
      id: string
      outcome: enum [success, failure, partial]
      task_desc: string
      key_errors: array[string]
      key_decisions: array[string]
      phase_reached: string
      high_quality: boolean
      relevance_score: float  # 0.0-1.0 (TF-IDF cosine or tag-based)
      scoring_method: enum [tfidf, tag_based]  # which method was used
      related_episodes: array[string]
      failure_patterns: array[object]
  total_episodes: integer
  method_used: enum [tfidf, tag_based]

load_error:
  code: enum [READ_FAILED, NO_EPISODES]
  message: string
  episodes: []
```

## Idempotency
- **SAVE**: Not idempotent — each call appends a new episode. Caller must avoid double-save.
  - Deduplication: if `sha256(ts + task_desc)[:16]` collides, log warning but do NOT overwrite.
- **LOAD**: Idempotent — read-only.

## Side Effects
- SAVE: appends to `.omc/episodes.jsonl`
- LOAD: read-only (no side effects)

## high_quality Criteria (explicit)
All three must be true:
1. `outcome == "success"`
2. All test commands returned exit code 0 (caller must verify and pass this as a known fact)
3. No CRITICAL/MAJOR issues in validation phase

If caller cannot verify test results, set `high_quality=false` (safe default).

## TF-IDF vs Tag-Based
- TF-IDF cosine: used when >= 5 episodes exist in store
- Tag-based: fallback when < 5 episodes (returns sorted by tag overlap score)
- `scoring_method` field in response tells caller which was used

## Dependencies
- Requires: write access to `.omc/episodes.jsonl`
- No external skill dependencies

## Downstream Consumers
- `live` / `live-inf` (PRE-LOOP step 1): loads past episodes
- `omc-autopilot` (Phase 5): saves completion summary
- `omc-failure-router` (caller): caller must invoke save on fatal classification

## Version Compatibility
- v1.0.0: Initial formal interface definition
