# Remote Notify Client Registry (Tailscale)

> **⭐ Install / fix popups (admin PS on Windows + Tailscale signed in):** `irm http://<WSL2-tailscale-ip>:9955/bootstrap | iex` — installs listener + firewall + URL ACL + S4U-persistent task. Re-run to fix broken popups, or locally: `Start-ScheduledTask -TaskName ClaudeNotifyListener`.
> Get WSL2 Tailscale IP: `tailscale ip -4` (run in WSL2)

> **TL;DR** — All clients bind `0.0.0.0:6789` (their own Tailscale IP). WSL2 hooks enumerate online Windows peers via `tailscale status --json` and POST directly to `http://{tailscale-ip}:6789/{notify,close,clipboard,expose,unexpose}`. No SSH tunnel, no port bookkeeping — each client's Tailscale IP is its own namespace.

**Listener endpoints on each client (port 6789):**
| Endpoint | Method | Purpose (Spec) |
|---|---|---|
| `/notify`, `/close`, `/health` | POST/GET | Popup (Spec 1) |
| `/clipboard` | POST | Clipboard sync (Spec 2) |
| `/expose`, `/unexpose`, `/exposed` | POST/GET | Dynamic same-URL dev-server mirror (Spec 3) |

**New client onboarding — 1 line (admin PowerShell on new PC, must be on Tailscale):**
```powershell
irm http://<WSL2-tailscale-ip>:9955/bootstrap | iex
# Get WSL2 IP first: run `tailscale ip -4` in WSL2
```
Script binds HttpListener on `0.0.0.0:6789`, registers URL ACL (`http://+:6789/`), adds Windows Firewall inbound rule, installs Task Scheduler auto-start with **RunLevel Highest** (required for netsh portproxy). Re-runnable on any client — no port collision.

**Spec 3 usage (dynamic dev-server mirror, no hardcoded port list):**
```bash
wsl-expose 3003    # all online Windows clients: localhost:3003 → WSL2 localhost:3003
wsl-unexpose 3003  # remove
```
Implementation: `/expose` endpoint runs `netsh interface portproxy add v4tov4 listenaddress=127.0.0.1 listenport=N connectaddress=<WSL2-tailscale-ip> connectport=N`. Requires listener to run as admin (Task `-RunLevel Highest`).

**Server infrastructure (WSL2, auto-starts via systemd):**
- `~/.claude/hooks/claude-client-bootstrap.py` — serves `/bootstrap` + static files
- Systemd user service: `claude-client-bootstrap.service` (enabled at `default.target`)
- CLI: `~/.local/bin/wsl-expose <port>`, `wsl-unexpose <port>`

**WSL2 hooks that fan out to clients:** `windows-notify.sh`, `windows-stop.sh`, `close-popup.sh`, `clip-to-remote.sh` — all enumerate via `tailscale status --json`.

Always start listener via `Start-ScheduledTask -TaskName ClaudeNotifyListener` (never `Start-Process` — dies on SSH close).

**Deploy updated listener:**
```bash
sed -n '30,265p' ~/.claude/hooks/client-setup-ps5.ps1 > /tmp/l.ps1 && scp /tmp/l.ps1 "<alias>:C:/Users/<user>/claude-notify-listener.ps1"
ssh <alias> 'powershell.exe -Command "Get-CimInstance Win32_Process -Filter \"Name='"'"'powershell.exe'"'"'\" | Where-Object { \$_.CommandLine -like \"*claude-notify-listener*\" } | ForEach-Object { Stop-Process -Id \$_.ProcessId -Force }; Start-Sleep 1; Start-ScheduledTask -TaskName ClaudeNotifyListener"'
```
