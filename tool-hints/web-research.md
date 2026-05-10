# Tool Hints: web-research
**Trigger**: external docs, library APIs, latest info lookup

## Priority
1. `WebSearch` — native Anthropic (Claude Code default)
2. `WebFetch` — fetch full URL content
3. `mcp__websearch__search_web` — non-Anthropic model fallback
4. `mcp__websearch__fetch_url` — non-Anthropic model URL fetch
5. `mcp__plugin_context7_context7__query-docs` — official library docs only

## Param patterns
```
WebSearch: query="topic site:docs.anthropic.com"
mcp__plugin_context7_context7__query-docs: libraryId="/anthropic/claude", query="tool use"
```

## Warning
- Only use URLs from user input or search results — never fabricate URLs
