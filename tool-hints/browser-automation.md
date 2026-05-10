# Tool Hints: browser-automation
**Trigger**: UI testing, screenshots, web app interaction, E2E validation

## Session selection (MANDATORY)
- Order: session-1 → 2 → 3 → 4
- Check `browser_tabs` first → `about:blank` = idle → reuse it
- Never create new sessions without authorization
- Login required → stop immediately, ask user

## Tool sequence
1. `browser_snapshot` — get current DOM + refs
2. `browser_navigate` — go to URL
3. `browser_click` — use ref from snapshot (never arbitrary CSS selectors)
4. `browser_fill_form` — form input
5. `browser_take_screenshot` — visual verification

## Param patterns
```
browser_click: {"ref": "e123"}  ← extract ref from snapshot
browser_navigate: {"url": "http://localhost:3000"}
```

## Note
- Stop Hook auto-runs Playwright validation when port 3000 detected
