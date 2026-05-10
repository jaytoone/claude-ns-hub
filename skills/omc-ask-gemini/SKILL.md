---
name: ask-gemini
description: "Ask Google Gemini via local CLI and capture a reusable artifact. Use for long-context analysis, multi-step reasoning, and knowledge synthesis where Gemini's large context window excels. Use ask-codex instead for pure code generation tasks."
---

# Ask Gemini

## Use When
- You want a second opinion from Gemini's perspective on any question or analysis
- Task requires large context (Gemini has a 1M token context window)
- Long document analysis, synthesis of multiple sources, or extended reasoning chains
- User says "ask gemini" or "gemini opinion"
- You need Google ecosystem integration (Google Docs, Sheets, Drive)

## Do Not Use When
- Gemini CLI is not installed (check with `gemini --version`) — fallback: use `omc-ask-codex`
- Task is primarily code generation (use `omc-ask-codex` — stronger code-first training)
- Task is research synthesis (use `expert-research` for structured multi-source analysis)
- You need multi-model orchestration (use `omc-ccg` for Claude+Codex+Gemini together)

## Fallback
If `gemini --version` fails: switch to `omc-ask-codex` or answer directly without external advisor.

---

Use Gemini as an external advisor through OMC's ask command.

## Usage

```bash
/oh-my-claudecode:ask-gemini <question or task>
```

## Routing

Preferred path:

```bash
omc ask gemini "{{ARGUMENTS}}"
```

Wrapper alias (compatibility):

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/ask-gemini.sh" "{{ARGUMENTS}}"
```

## Requirements

- Local Gemini CLI must be installed and authenticated.
- Verify with:

```bash
gemini --version
```

## Artifacts

`omc ask` writes artifacts to:

```text
.omc/artifacts/ask/gemini-<slug>-<timestamp>.md
```

Task: {{ARGUMENTS}}
