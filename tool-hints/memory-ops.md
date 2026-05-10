# Tool Hints: memory-ops
**Trigger**: persist knowledge across sessions, restore prior decisions

## Tool selection
| Purpose | Tool |
|---------|------|
| Restore context on session start | `mcp__memory__read_graph` |
| Store new knowledge | `mcp__memory__create_entities` |
| Store relations | `mcp__memory__create_relations` |
| Keyword search | `mcp__memory__search_nodes` |
| Store patterns | `mcp__claude-flow__hooks_intelligence_pattern-store` |
| Search patterns | `mcp__claude-flow__hooks_intelligence_pattern-search` |

## Save criteria (selective only)
- ✅ TechnicalDecision, OpenIssue, EnvTrap, ReusablePattern
- ❌ One-off task plans, completed task details

## Param patterns
```json
mcp__memory__create_entities:
{"entities": [{"name": "...", "entityType": "TechnicalDecision", "observations": ["..."]}]}

mcp__memory__search_nodes: {"query": "natural language query"}
```

## Broken (do not use)
- `mcp__agentdb_pattern-store` / `mcp__agentdb_pattern-search` — "Bridge not available"
