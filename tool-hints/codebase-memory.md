# Tool Hints: codebase-memory-mcp
**AUTO-TRIGGER**: fire automatically — no user instruction needed

## When to auto-invoke
- "who calls X" / "what calls X" / "call chain" / "trace dependency"
- Exploring module architecture or relationships
- Impact analysis before refactoring
- "where is X defined/implemented" (graph search, not text search)

## When NOT to use
- Exact text/string search → use Grep
- Reading a specific file → use Read
- File pattern matching → use Glob

## Tool priority (within codebase-memory)
1. `search_graph` — find nodes by name/pattern (fuzzy, label filters)
2. `trace_call_path` — inbound/outbound call chain traversal
3. `get_code_snippet` — read function source (replaces Read for functions)
4. `get_architecture` — high-level project summary
5. `query_graph` — Cypher query (advanced, use when above insufficient)

## Param patterns
```
search_graph: {"pattern": "functionName", "label": "Function", "limit": 10}
trace_call_path: {"node_id": "...", "direction": "both", "depth": 3}
get_architecture: {"project_path": "/home/jayone/Project/AgentNode"}
```

## Setup (if index missing)
```
index_repository: {"project_path": "/home/jayone/Project/AgentNode"}
index_status: {}  # check progress
```
