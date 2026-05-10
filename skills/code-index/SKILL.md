---
name: code-index
description: "Codebase Semantic Indexing Skill — Uses code-search MCP (local FAISS + sentence-transformers) to index projects and search code with natural language. Replaces repomix: selectively loads only relevant files without loading full context. Triggers: 'codebase indexing', 'index it', 'index codebase', 'code search', 'search code', 'find similar code'"
trigger: manual
tags:
  - code-search
  - indexing
  - semantic-search
  - mcp
  - faiss
  - context-management
---

# code-index: Codebase Semantic Indexing & Search

Uses the `code-search` MCP server (local FAISS + `all-MiniLM-L6-v2`) to index projects as vector embeddings and search for relevant code using natural language.

**Purpose**: Instead of loading full context via repomix, selectively search for only task-relevant code to maximize context efficiency.

---

## MCP Server Information

- **Server name**: `code-search`
- **Location**: `~/.local/share/claude-context-local/`
- **Embedding model**: `all-MiniLM-L6-v2` (local, 384 dimensions, ~90MB)
- **Vector DB**: FAISS (local file)
- **No API key required**

---

## Available Tools (Load via ToolSearch before use)

| Tool Name | Purpose |
|-----------|---------|
| `index_directory(path)` | Index an entire directory with embeddings |
| `search_code(query, k=5)` | Search for relevant code with natural language queries |
| `find_similar_code(chunk_id, k=5)` | Find code similar to a specific code chunk |
| `get_index_status()` | Check current index status/statistics |
| `list_projects()` | List indexed projects |
| `switch_project(path)` | Switch to a different indexed project |

---

## Step 1: Load Tools

```
ToolSearch("select:mcp__code-search__index_directory")
ToolSearch("select:mcp__code-search__search_code")
ToolSearch("select:mcp__code-search__get_index_status")
```

> If MCP tool names are not yet confirmed: search with ToolSearch("code search index")

---

## Step 1.5: Switch Project (Always execute)

Always switch to the current working directory's project before calling `search_code()`.

```python
ToolSearch("select:mcp__code-search__switch_project")
→ switch_project(PROJECT_ROOT)   # Current Claude session's project path
  # If PROJECT_ROOT is unknown: switch_project("/home/jayone/Project/ASI")
```

> **Reason**: The code-search MCP has a global multi-project index.
> When the session changes, the active project resets to `claude-context-local`.
> If you don't switch before `search_code()`, it will search in the wrong project.

---

## Step 2: Check Index Status + Quality Inspection

```python
get_index_status()
```

### Inspection Criteria (all must pass to proceed to Step 4)

| Item | Criterion | On Failure |
|------|-----------|------------|
| `project_path` | Matches CWD (current working directory) | Step 3 full re-indexing |
| `total_chunks` | >= 1,000 | Step 3 full re-indexing |
| `top_tags` | Project language (python/typescript, etc.) exists | Step 3 full re-indexing |
| `index_type` | `IndexIVFFlat` or `IndexFlatIP` | Step 3 full re-indexing |

**Decision Logic**:
```
Check get_index_status() results:
  ├─ project_path ≠ CWD → Re-indexing needed
  ├─ total_chunks < 1000 → Re-indexing needed (detects corrupted indexes like 272 chunks)
  ├─ top_tags missing project's main language → Re-indexing needed
  └─ All above pass → Proceed to Step 4 (search)
```

> **Real-world case**: total_chunks=272 (normal: 22,389) → If used without re-indexing,
> core files like `train_hf_multifile_full.py` would not have been searchable.

---

## Step 3: Project Indexing

```python
# Index the current project directory
index_directory(
    "/home/jayone/Project/ASI",  # Use actual CWD
    project_name="ASI",
    incremental=False  # False for full re-indexing, True for incremental
)
```

**Duration**: Seconds to minutes depending on file count
**Excluded from indexing**: `node_modules/`, `.git/`, `__pycache__/`, `dist/`, `.next/`

### Incremental Indexing (when some files changed)
```python
index_directory("/path/to/project", incremental=True)
```

---

## Step 4: Code Search

### Basic Search
```python
search_code("training loop loss calculation")
# Default k: 5 results
```

### Precise Search
```python
search_code("DDP initialization setup", k=10, file_pattern="*.py")
search_code("React component state management", k=5, file_pattern="*.tsx")
```

### Output Format
```
Result 1: src/training/loss.py (lines 45-78) [similarity: 0.89]
  def calculate_loss(outputs, targets, weights):
      ...
```

---

## Step 5: Similar Code Exploration

```python
# Use chunk_id from search_code results
find_similar_code("src/training/loss.py:45-78:function:calculate_loss", k=5)
```

---

## Usage Scenarios

### Scenario 1: Understanding context before implementing a new feature
```
1. search_code("authentication middleware")
2. Load only 3-5 relevant files with Read
3. Understand patterns, then implement
→ 90% context savings compared to repomix full load
```

### Scenario 2: Finding related code during bug fixing
```
1. search_code("error message text")
2. find_similar_code(that chunk_id)
3. Selectively load only related functions
```

### Scenario 3: Finding duplicate code before refactoring
```
1. search_code("specific pattern")
2. Use find_similar_code to explore similar implementations
3. Identify consolidation targets
```

---

## Troubleshooting

### MCP server not responding
```bash
# Test server directly
uv run --directory ~/.local/share/claude-context-local python mcp_server/server.py
```

### Indexing error (model download failure)
```bash
# Check if sentence-transformers model is in cache
ls ~/.cache/huggingface/hub/ | grep MiniLM
# If missing: pip install sentence-transformers
```

### Empty search results
- Verify indexing completed: `get_index_status()`
- Make the query more specific
- Increase `k` value for more results

---

## Installation Information (Reference)

- **MCP registration**: `~/.claude.json` → `code-search` entry
- **Patched files**:
  - `~/.local/share/claude-context-local/embeddings/embedding_models_register.py`
  - `~/.local/share/claude-context-local/embeddings/sentence_transformer.py`
  - `~/.local/share/claude-context-local/embeddings/embedder.py`
- **Patch reason**: Default model `google/embeddinggemma-300m` is gated (HF access unavailable) → Replaced with `all-MiniLM-L6-v2`
