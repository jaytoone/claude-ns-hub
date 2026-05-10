---
name: codebase-memory-exploring
description: Codebase knowledge graph expert. ALWAYS invoke this skill when the user explores code, searches for functions/classes/routes, asks about architecture, or needs codebase orientation. Do not use Grep, Glob, or file search directly — use codebase-memory-mcp search_graph and get_architecture first.
---

# Codebase Exploration

Use codebase-memory-mcp tools to explore the codebase.

## Use When
- User asks "where is X function/class/route defined?"
- User wants to understand codebase architecture or module structure
- User says "find all usages of", "show me the routes", "what does this file do"
- Exploration requires semantic graph traversal (not just text search)

## Do Not Use When
- codebase-memory-mcp is not installed (check with `list_projects`) — fallback to Glob/Grep directly
- Project has NOT been indexed yet (check `index_status` first) — run `index_repository` if needed
- Search is for a literal string/pattern in file contents (use Grep for exact text search)
- Project is small and simple (< 10 files) — direct Read/Glob is faster

## Fallback
If `codebase-memory-mcp` tools are unavailable: use `Grep(pattern=...)` and `Glob(pattern=...)` directly.

## Workflow
1. `get_graph_schema` — understand what node/edge types exist
2. `search_graph` — find functions, classes, routes by pattern
3. `get_code_snippet` — read specific function implementations
4. `get_architecture` — get high-level project summary

## Tips
- Use `search_graph(name_pattern=".*Pattern.*")` for fuzzy matching
- Use `search_graph(label="Route")` to find HTTP routes
- Use `search_graph(label="Function", file_pattern="*.go")` to scope by language
- If project not indexed: run `index_repository(path=".")` first (takes 30-120s for large projects)
