# Research: Suppressing Stop Hook terminal UI output

> Written: 2026-02-21 | Reference: https://code.claude.com/docs/en/hooks

## Problem

When a Stop Hook returns `decision: "block"` + `reason`, the entire `reason`
string is surfaced in the terminal UI.

## Findings from the official docs

### Relevant fields

| Field | Default | Effect |
|-------|---------|--------|
| `suppressOutput` | `false` | When `true`, hides stdout from verbose mode (Ctrl+O). **Does not hide `reason` itself.** |
| `reason` | — | With `decision: "block"`, displayed directly in the terminal UI. **No official way to hide it.** |
| `continue` | `true` | When `false`, terminates Claude entirely. |
| `stopReason` | — | Message shown to the user when `continue: false` (not visible to Claude). |

### Conclusion

**There is no official way to fully hide the `reason` field when `decision: "block"` is used.**

`suppressOutput: true` only controls stdout-verbose visibility; it has no effect
on `reason` exposure.

---

## Applied solution (Solution A: minimize `reason`, move details to CLAUDE.md)

### Before

```
stop-hook-instructions.md = 39-line detailed guide (with ━━━ dividers)
→ All 39 lines leaked into the reason field and shown in the terminal UI.
```

### After

```
stop-hook-instructions.md = only the 3-line trigger message
→ Only 3 lines appear in the reason field.

Detailed procedure → moved to the "Stop Hook - Playwright verification procedure"
section of ~/.claude/CLAUDE.md
→ Claude already knows the procedure at session start.
```

### Affected files

1. `~/.claude/hooks/stop-hook-instructions.md` — shortened to 3 lines
2. `~/.claude/hooks/stop-playwright-validation.sh` — added `suppressOutput: true`
3. `~/.claude/CLAUDE.md` — added the Playwright verification procedure section

---

## Alternative solutions (not applied)

### Solution B: switch to a `type: "prompt"` hook

```json
{
  "hooks": {
    "Stop": [{
      "hooks": [{
        "type": "prompt",
        "prompt": "If the flag file {flag} is missing, perform Playwright verification at {url}. $ARGUMENTS",
        "timeout": 120
      }]
    }]
  }
}
```

- Claude evaluates directly and returns `{"ok": false, "reason": "..."}`.
- Terminal UI rendering may differ, but this is not verified.
- Downside: every Stop triggers a Haiku API call (cost).

### Solution C: switch to a `type: "agent"` hook

```json
{
  "hooks": {
    "Stop": [{
      "hooks": [{
        "type": "agent",
        "prompt": "Perform Playwright verification, then return ok/not-ok. $ARGUMENTS",
        "timeout": 180
      }]
    }]
  }
}
```

- A subagent runs Playwright verification directly.
- Minimizes terminal UI output.
- Downside: every Stop spawns a subagent (overhead).

---

## References

- [Hooks Reference](https://code.claude.com/docs/en/hooks) — JSON output fields section
- Stop decision control: `decision`, `reason` fields
- `suppressOutput` official behavior: "hides stdout from verbose mode output"
