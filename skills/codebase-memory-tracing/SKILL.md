---
name: codebase-memory-tracing
description: Call chain and dependency expert. ALWAYS invoke this skill when the user asks who calls a function, what a function calls, needs impact analysis, or traces dependencies. Do not grep for function names directly — use codebase-memory-mcp trace_call_path first.
---

# Call Tracing & Impact Analysis

Use codebase-memory-mcp tools to trace call paths.

## Use When
- User asks "who calls X?", "what does X call?", "what will break if I change X?"
- Impact analysis before refactoring or deleting a function
- User says "trace", "call chain", "dependency path", "upstream/downstream"
- Understanding data flow between components

## Do Not Use When
- codebase-memory-mcp not installed or project not indexed — fallback to Grep for function name
- You need cross-file text search (not semantic graph traversal) — use Grep directly
- You need import dependency analysis in a language not supported by the graph schema

## Fallback
If graph tools unavailable: `Grep(pattern="functionName", output_mode="files_with_matches")` to find call sites manually.

## Workflow
1. `search_graph(name_pattern=".*FuncName.*")` — find exact function name
2. `trace_call_path(function_name="FuncName", direction="both")` — trace callers + callees
3. `detect_changes` — find what changed and assess risk_labels

## Direction Options
- `inbound` — who calls this function? (impact analysis: "what breaks?")
- `outbound` — what does this function call? (dependency analysis: "what does this need?")
- `both` — full context before any refactor
