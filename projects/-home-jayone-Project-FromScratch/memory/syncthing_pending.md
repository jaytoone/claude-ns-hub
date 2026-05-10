---
name: Syncthing toomu pairing pending
description: WSL2 Syncthing is set up; toomu side install+pairing deferred to tomorrow (2026-04-28)
type: project
originSessionId: 429d4525-93b5-4802-a603-5e2d1f6aee1d
---
Syncthing WSL2 side is fully configured and running. toomu pairing is pending.

**Why:** User deferred toomu setup to tomorrow (2026-04-28).

**How to apply:** At session start, remind user to complete Syncthing toomu pairing.

## WSL2 Status (DONE)
- Service: `systemctl --user status syncthing` — running
- GUI: `http://100.66.30.40:8384` — user: `jayone`, password: `QgbRy6eA6pT2i+EbLoU+Cg==`
- Folder: `claude-inbox` → `~/claude-inbox/` (receive-only, Folder ID: `claude-inbox`)
- HTTP server: `http://100.66.30.40:8765/` (read-only, Tailscale-only)
- WSL2 Device ID: `XNRSWCK-36AXSUQ-AQ5NY3H-PXS4RJQ-2IUBKVV-P6JTRSA-VMHKJCN-YWS5OAZ`

## toomu TODO (2026-04-28)
1. Download Syncthing Windows: https://syncthing.net/downloads/
2. Run `syncthing.exe` → `http://127.0.0.1:8384` on toomu
3. Add Remote Device → paste WSL2 Device ID above
4. Add Folder → `C:\Users\toomu\claude-inbox`, Folder ID: `claude-inbox`, share with WSL2
5. Accept popup in WSL2 Syncthing UI

## Reference doc
`docs/research/20260427-syncthing-toomu-setup-pending.md`
