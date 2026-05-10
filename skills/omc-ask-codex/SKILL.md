---
name: ask-codex
description: "Ask OpenAI Codex via local CLI and capture a reusable artifact. Use for code generation, refactoring, and agentic coding tasks where Codex's code-first training excels. Use ask-gemini instead for long-context analysis, multi-step reasoning, or Google ecosystem tasks."
---

# Ask Codex

## Use When
- You want a second opinion on code implementation from a model with strong code-first training
- Task is primarily code generation, refactoring, or code completion
- User says "ask codex" or "codex opinion"
- You want to cross-validate Claude's implementation with an external model

## Do Not Use When
- Codex CLI is not installed (check with `codex --version`) — fallback: use `omc-ask-gemini`
- Task requires long-context document analysis (use `omc-ask-gemini` — higher context window)
- Task is research or knowledge synthesis (use `expert-research` instead)
- You need multi-model orchestration (use `omc-ccg` for Claude+Codex+Gemini together)

## Fallback
If `codex --version` fails: switch to `omc-ask-gemini` or answer directly without external advisor.

---

Use Codex as an external advisor through OMC's ask command.

## Usage

```bash
/oh-my-claudecode:ask-codex <question or task>
```

## Routing

Preferred path:

```bash
omc ask codex "{{ARGUMENTS}}"
```

Wrapper alias (compatibility):

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/ask-codex.sh" "{{ARGUMENTS}}"
```

## Requirements

- Local Codex CLI must be installed and authenticated.
- Verify with:

```bash
codex --version
```

## Artifacts

`omc ask` writes artifacts to:

```text
.omc/artifacts/ask/codex-<slug>-<timestamp>.md
```

Task: {{ARGUMENTS}}
