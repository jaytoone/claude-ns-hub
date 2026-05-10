# Skill Interface: expert-research-v2
# Version: 1.0.0
# Last updated: 2026-04-09

## Input Contract

```yaml
required:
  question:
    type: string
    description: "The research question or topic to investigate"
    min_length: 10
    max_length: 2000

optional:
  mode:
    type: enum
    values: [full, lightweight]
    default: full
    description: "full=3-agent with DA; lightweight=skip DA for speed (simple questions only)"
  save_path:
    type: string
    description: "Override default doc save path (default: docs/research/YYYYMMDD-topic.md)"
  context:
    type: string
    description: "Additional context to inject into all agent prompts"
    max_length: 4000
```

## Output Contract

```yaml
success:
  answer:
    type: string
    description: "Final synthesized answer (CONFIRMED-STRONG items first)"
  consensus_matrix:
    type: object
    description: "Cross-validation results per claim"
    fields:
      confirmed_strong: [string]
      strong: [string]
      contested: [string]
      rejected: [string]
      unresolved: [string]
  sources:
    type: array
    items:
      type: object
      fields:
        url: string
        tier: enum [S1, S2, S3, S4]
        claim: string
  saved_doc_path:
    type: string
    description: "Path where research was saved (always set on success)"
  confidence:
    type: float
    range: [0.0, 1.0]
    description: "Proportion of claims that are CONFIRMED-STRONG or STRONG"

failure:
  error:
    type: enum
    values:
      - AGENT_FAILURE         # one of the 3 agents returned no output
      - SAVE_FAILED           # doc could not be written (check docs/ permissions)
      - QUESTION_TOO_VAGUE    # question cannot be researched without clarification
  message: string
  partial_results:
    type: object
    description: "Available results from agents that did complete (may be empty)"
```

## Idempotency
- **NOT idempotent**: Each invocation launches new web searches; results may differ.
- Safe to retry on AGENT_FAILURE; results will vary.

## Side Effects
- Writes to `docs/research/` (MANDATORY — pipeline is incomplete without this)
- Updates `docs/DOC_INDEX.md`
- Makes external web requests (Fact Finder)

## Dependencies
- Requires: `research-deep-analyst`, `review-harsh-critic`, `research-doc-specialist` agents
- Requires: WebSearch/WebFetch tools (Fact Finder phase)
- Requires: File write access to `docs/`

## Downstream Consumers
- `live` / `live-inf`: Wave 1 specialist for `task_type=research`
- `expert-research` (v1): predecessor, not a consumer
- Any skill needing external fact-grounding

## Handoff To (outputs consumed by)
| Downstream Skill | Condition | Data Passed |
|-----------------|-----------|-------------|
| `live-inf` (Wave 2) | When used as Wave 1 specialist | `answer` + `sources` injected into context_primer |
| User directly | Default | Full synthesis output |

## Version Compatibility
- v1.0.0: Initial formal interface definition
- Breaking change policy: increment major version; maintain v(N-1) shim for 90 days
