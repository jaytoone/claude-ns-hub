# claude-client-bootstrap

WSL2 → Windows notification + clipboard + browser tunnel + noVNC, over Tailscale.

One-line Windows client onboarding (admin PowerShell, must be on tailnet):
```powershell
irm http://<wsl2-tailscale-ip>:9955/bootstrap | iex
```

## What it sets up

| Spec | What | Port |
|------|------|------|
| 1 — Popup | Claude start/stop → WinForms square on Windows taskbar | 6789/notify |
| 2 — Clipboard | WSL2 copy → Windows clipboard | 6789/clipboard |
| 3 — Browser tunnel | `wsl-expose <port>` → `localhost:<port>` on Windows | 6789/expose |
| 4 — noVNC | Playwright browser visible/controllable from Windows | 6901 + 8831 |

## WSL2 server install (after backup/restore)

```bash
git clone https://github.com/jaytoone/claude-client-bootstrap
cd claude-client-bootstrap
bash install.sh
```

`install.sh` copies files to `~/.claude/hooks/` and `~/.local/bin/`, enables the systemd service, and prints the onboarding URL.

## Prerequisites

- Tailscale running on WSL2 and all Windows clients
- `jq` on WSL2: `sudo apt install jq`
- Docker Desktop with WSL2 integration enabled (Spec 4 only)
  - Docker Desktop → Settings → Resources → WSL Integration → enable your distro

## File layout

```
server/
  claude-client-bootstrap.py      # HTTP server, port 9955, auto-detects Tailscale IP
  claude-client-bootstrap.service # systemd user service
hooks/
  windows-notify.sh               # Spec 1: Claude start hook
  windows-stop.sh                 # Spec 1: Claude stop hook
  close-popup.sh                  # Spec 1: dismiss popup on next prompt
client/
  client-setup-ps5.ps1            # Spec 1+2+3: Windows listener installer
bin/
  wsl-expose                      # Spec 3: mirror WSL2 port to Windows localhost
  wsl-unexpose                    # Spec 3: remove mirror
  clip-to-remote.sh               # Spec 2: zellij copy_command target
novnc/
  docker-compose.yml              # Spec 4: Playwright noVNC container
  wsl-novnc-start                 # Spec 4: start container + expose ports
  wsl-novnc-stop                  # Spec 4: stop + unexpose
```

## Spec 1 — Popup notifications

Claude Code hooks call `windows-notify.sh` (on start) and `windows-stop.sh` (on stop).
Each hook enumerates online Windows tailnet peers via `tailscale status --json` and POSTs
to `http://<peer-ip>:6789/notify`. The Windows listener shows a WinForms square popup.

Required env var in `~/.claude/settings.json`:
```json
{ "env": { "CLAUDE_REMOTE_NOTIFY_URL": "1", "CLAUDE_REMOTE_NOTIFY_ONLY": "1" } }
```

## Spec 2 — Clipboard sync

Set zellij `copy_command` to `~/.local/bin/clip-to-remote.sh`. On copy, it POSTs the
content to all online Windows peers at `:6789/clipboard`.

## Spec 3 — Browser tunnel

```bash
wsl-expose 3003    # localhost:3003 on all Windows clients now reaches WSL2:3003
wsl-unexpose 3003
```

Requires the Windows listener to run as admin (Task Scheduler `-RunLevel Highest`, set by `client-setup-ps5.ps1`).

## Spec 4 — noVNC Playwright

```bash
./novnc/wsl-novnc-start
# Open http://localhost:6901 in Windows browser — live browser view
# Claude Code MCP: http://localhost:8831/sse
```

Claude Code `.mcp.json`:
```json
{
  "mcpServers": {
    "playwright": { "type": "sse", "url": "http://localhost:8831/sse" }
  }
}
```
