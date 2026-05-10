---
name: codebase-memory-quality
description: Code quality analysis expert. ALWAYS invoke this skill when the user asks about dead code, unused functions, complexity, refactor candidates, or cleanup opportunities. Do not search files manually — use codebase-memory-mcp search_graph with degree filters first.
---

# Code Quality Analysis

Use codebase-memory-mcp tools for quality analysis.

## Use When
- User asks about dead code, unused functions, or cleanup opportunities
- User says "find complex functions", "what can I refactor", "show me code smells"
- Impact analysis before deleting or refactoring code
- Finding the highest-complexity entry points for review

## Do Not Use When
- codebase-memory-mcp is not installed or project not indexed — use Grep + manual analysis
- User wants static type or lint analysis — use `omc-build-fix` or `omc-code-review` instead
- User wants security quality analysis — use `omc-security-review` instead

## Fallback
If graph tools unavailable: use `Grep(pattern="def |function |class ")` to find symbols, then manually assess coupling.

## Dead Code Detection
- `search_graph(max_degree=0, exclude_entry_points=true)` — find unreferenced functions
- `search_graph(max_degree=0, label="Function")` — unreferenced functions only

## Complexity Analysis
- `search_graph(min_degree=10)` — high fan-out functions (possible God objects)
- `search_graph(label="Function", sort_by="degree")` — most-connected functions
- High in-degree = widely used (risky to change); high out-degree = complex orchestrators (refactor candidates)
