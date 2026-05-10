# Tool Hints: cort (Recursive Deep Reasoning)
**AUTO-TRIGGER**: fire automatically — no user instruction needed

## When to auto-invoke
- User asks: "should I", "is it better to", "compare X vs Y", "best approach for"
- Architecture decisions with multiple tradeoffs
- Complex debugging with 3+ possible root causes
- Algorithm selection, design pattern choices
- Multi-step logical reasoning chains

## When NOT to use
- Simple factual lookups
- Straightforward code edits
- Single-step tasks

## Tool selection
| Use case | Tool |
|----------|------|
| Quick answer needed | `mcp__cort__cort_think_simple` |
| Full reasoning trace | `mcp__cort__cort_think_details` |
| Cross-model comparison | `mcp__cort__cort_think_simple_mixed_llm` |

## Param pattern
```
mcp__cort__cort_think_simple: {"prompt": "full question with context"}
mcp__cort__cort_think_details: {"prompt": "full question with context"}
```

## Note
- Include full context in prompt (cort has no conversation history)
- cort_think_details returns YAML-format reasoning trace
