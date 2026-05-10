# Tool Hints: code-search
**AUTO-TRIGGER conditions defined below**

## Auto-invoke vs Grep decision tree
```
Query is exact text/function name? → Grep (faster)
Query is conceptual / natural language? → mcp__code-search__search_code
Grep returns 0 results for concept query? → mcp__code-search__search_code
"find all places that handle X" → mcp__code-search__search_code
```

## Priority
1. `Grep` — exact text/regex (always try first)
2. `Glob` — file pattern matching
3. `Read` — specific file
4. `mcp__code-search__search_code` — natural language semantic (T1 insufficient)
5. `mcp__code-search__index_directory` — run first if no index

## Param patterns
```
Grep: pattern="functionName", path="src/", type="ts"
mcp__code-search__search_code: query="natural language description", project_path="/home/jayone/Project/..."
mcp__code-search__index_directory: {"project_path": "/home/jayone/Project/AgentNode", "incremental": true}
```

## Never use
- `mcp__obsidian__*` for codebase search (banned)
