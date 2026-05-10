---
name: codebase-memory-reference
description: Codebase-memory-mcp reference guide. ALWAYS invoke this skill when the user asks about MCP tools, graph queries, Cypher syntax, edge types, or how to use the knowledge graph. Do not guess tool parameters — load this reference first.
---

# Codebase Memory MCP Reference

## Use When
- You need to look up exact tool names, parameters, or edge type names for codebase-memory-mcp
- User asks "how do I query the graph?", "what are the edge types?", "show me Cypher examples"
- You're about to use a codebase-memory-mcp tool and need to confirm parameter syntax

## Do Not Use When
- You don't have codebase-memory-mcp installed — check with `list_projects` first
- User is asking about a different MCP tool (unrelated to codebase graph queries)

## First Steps for New Projects
1. Run `list_projects` — see if the project is already indexed
2. If not: run `index_repository(path=".")` — takes 30-120s depending on repo size
3. Check progress with `index_status`
4. Then use `search_graph`, `trace_call_path`, etc.

---

## 14 total MCP Tools
- `index_repository` — index a project
- `index_status` — check indexing progress
- `detect_changes` — find what changed since last index
- `search_graph` — find nodes by pattern
- `search_code` — text search in source
- `query_graph` — Cypher query language
- `trace_call_path` — call chain traversal
- `get_code_snippet` — read function source
- `get_graph_schema` — node/edge type catalog
- `get_architecture` — high-level summary
- `list_projects` — indexed projects
- `delete_project` — remove a project
- `manage_adr` — architecture decision records
- `ingest_traces` — import runtime traces

## Edge Types
CALLS, HTTP_CALLS, ASYNC_CALLS, IMPORTS, DEFINES, DEFINES_METHOD,
HANDLES, IMPLEMENTS, CONTAINS_FILE, CONTAINS_FOLDER, CONTAINS_PACKAGE

## Cypher Examples
```
MATCH (f:Function) WHERE f.name =~ '.*Handler.*' RETURN f.name, f.file_path
MATCH (a)-[r:CALLS]->(b) WHERE a.name = 'main' RETURN b.name
MATCH (a)-[r:HTTP_CALLS]->(b) RETURN a.name, b.name, r.url_path
```
