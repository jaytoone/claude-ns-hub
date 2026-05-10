# Tool Hints: agent-orchestration
**Trigger**: multi-agent execution, parallel tasks, workflow automation

## Priority: Task() native > claude-flow MCP

### Task() — always prefer
```
Task(subagent_type="dev-executor", prompt="...")
Task(subagent_type="research-explore", model="haiku", prompt="...")
Task(subagent_type="review-verifier", prompt="...")
```
Independent tasks: call multiple Task() simultaneously.

### claude-flow MCP (only when Task() insufficient)
| Purpose | Tool |
|---------|------|
| Spawn agent | `mcp__claude-flow__agent_spawn` |
| Create task | `mcp__claude-flow__task_create` |
| Save session | `mcp__claude-flow__session_save` |
| Restore session | `mcp__claude-flow__session_restore` |
| System health | `mcp__claude-flow__system_health` |

## Broken (do not use)
- `mcp__analyze_diff*` — "require is not defined" (ESM/CJS conflict)
- ✅ Replacement: `mcp__claude-flow__analyze_file-risk`
