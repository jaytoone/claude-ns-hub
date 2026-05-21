## Current State (2026-05-19)

### WSL2 Security Hardening — Port Audit & Lockdown (2026-05-19, updated)
- **Active listeners (final state 2026-05-19 14:45 KST):**
  - `100.119.82.4:9000` — hub HTTP (`hub.service`, enabled+running, Tailscale-only) — tailpeers connect here
  - `100.119.82.4:8989` — Entity Dashboard (Tailscale-only; server.py default patched to 100.119.82.4)
  - `0.0.0.0:22` — sshd (key-auth only, low risk)
  - `0.0.0.0:3000` — Next.js dev (HugwartsBanana, not bootstrap, dev artifact)
- **Disabled/killed:**
  - `claude-inbox-httpd.service` (8765) — disabled
  - `hub-https.service` (9443) — disabled + process killed
  - `gdrive-vault.timer` — disabled
  - `hub.service` was re-enabled with correct `HUB_HOST=100.119.82.4` binding (env file)
- **LT-1 bootstrap artifacts removed:** ClaudeNotifyListener scheduled task deleted (VBS/PS1 already gone)
- **LT-3:** offline during cleanup — bootstrap artifacts pending removal on next online session
- **entity dashboard server.py fix:** default changed from `"0.0.0.0"` → `"100.119.82.4"` at `~/.claude/skills/entity/dashboard/server.py:29`
- Precise audit docx: https://drive.google.com/open?id=1hZQkV87iP_6TJ3d4f-258-2j3vMyVXxO

### Codex CLI Investigation (2026-05-19, M12)
- **Finding:** Codex CLI v0.131.0 IS installed (`~/.codex/`), model=`gpt-5.4-mini`, auth=ChatGPT OAuth
- **Trigger:** NOT caused by OpenRouter/OWL model chain. Caused by `omc-teams`/`omc-team` skills (oh-my-claudecode plugin) + `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` setting — CC spawns Codex CLI workers for code sub-tasks
- **Alias:** `xsk='codex --sandbox danger-full-access'` in `~/.bashrc`
- **zellij-csk.sh:** has `codex` backend but only triggers when `SESSION_BACKEND=codex` explicitly set
- **To prevent:** unset `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` or disable omc-teams/omc-team skills

### LT-1 Boot Investigation (2026-05-19)
- LT-1 was offline May 18 08:30 KST → May 19 10:17 KST (26 hours)
- Reboot reason: user-initiated shutdown via StartMenuExperienceHost after Windows Update staged KB777778 — NOT an auto-reboot
- M3 policy verified active: NoAutoRebootWithLoggedOnUsers=1, AlwaysAutoRebootAtScheduledTime=0
- Fixed UX ActiveHours: was 10-2 (wrong), corrected to 6-23 (matches policy)
- ActiveHours policy: Start=6, End=23, SmartActiveHoursState=0

## Current State (2026-05-14)

### LT-1 → WSL VS Code Remote-SSH BOM Fix (2026-05-14)
- Symptom: VS Code Remote-SSH from LT-1 fails with `Bad configuration option: \357\273\277host` — `~/.ssh/config` line 1 had UTF-8 BOM (`EF BB BF`) injected.
- Root cause: `client-setup-ps5.ps1` line 452 used `Set-Content -Encoding UTF8`; on Windows PowerShell 5.1 that flag emits UTF-8 **with** BOM. OpenSSH rejects the BOM'd first token and aborts before connecting.
- LT-1 config also still contained `RemoteForward 6789 127.0.0.1:6789` — that machine was last bootstrapped before the 2026-05-13 template patch and never re-run; the May-13 regex strip never fired on it.
- Fixed on LT-1 in place: BOM stripped + `RemoteForward 6789` line removed via `[System.IO.File]::WriteAllText` with `UTF8Encoding($false)`. Backup at `~/.ssh/config.bak-bom-*`. Verified `ssh -o BatchMode=yes home-wsl` returns `SSH_OK` from LT-1.
- Patched `~/.claude/hooks/client-setup-ps5.ps1` lines 448-455: (a) read with `[System.IO.File]::ReadAllText` so .NET auto-strips any pre-existing BOM, (b) strip-block regex switched to `(?ms)^Host home-wsl\b.*?(?=^Host \S|\z)` so it matches even when `home-wsl` is the FIRST entry (no leading newline), (c) write via `WriteAllText(...,[System.Text.Encoding]::ASCII)` since SSH config is pure ASCII — matches the line-105 pattern and is BOM-immune.
- Bootstrap server (`claude-client-bootstrap.py`, port 9955) serves the patched file on next `irm | iex` — no service restart needed (SimpleHTTPRequestHandler reads on each request).
- Left alone: line 341 `Set-Content -Encoding UTF8` for the notify listener `.ps1` — PowerShell itself tolerates a BOM in its own scripts.
- Stale copy at `~/.claude/client/client-setup-ps5.ps1` (Apr 29) is NOT served — the bootstrap reads only from `~/.claude/hooks/`. Safe to ignore for now.

### `msk` alias — Claude Code on MiniMax (2026-05-14)
- `~/.local/bin/msk`: uses `env -i` (fully clean environment) to avoid inheriting any tokens. Sets `ANTHROPIC_BASE_URL=https://api.minimax.io/anthropic`, models `MiniMax-M2.5` (sonnet/haiku) + `MiniMax-M2.7` (opus). Key baked into script.
- Key fix: unset `ANTHROPIC_AUTH_TOKEN` conflict resolved by switching to `env -i` clean environment. Verified `msk -p "ping"` → "pong".

### `orsk` alias — Claude Code on OpenRouter (2026-05-14)
- `~/.local/bin/orsk`: direct connection (no proxy), sets `ANTHROPIC_BASE_URL=https://openrouter.ai/api` (no `/v1` suffix — Claude Code appends it). Uses `ANTHROPIC_AUTH_TOKEN` (not `ANTHROPIC_API_KEY` — unsets the latter to avoid conflict). Models: `anthropic/claude-sonnet-4-6`, `claude-opus-4-7`, `claude-haiku-4-5`.

### `osk` alias — Claude Code on OpenAI GPT (parallel-safe with `csk`)
- Created `~/.local/bin/osk` (executable): auto-starts LiteLLM proxy on `127.0.0.1:4100`, then `exec`s `claude --dangerously-skip-permissions` with `CLAUDE_CODE_OAUTH_TOKEN=""`, `ANTHROPIC_BASE_URL=http://127.0.0.1:4100`, `ANTHROPIC_API_KEY=sk-osk-local`, `ANTHROPIC_MODEL=gpt-5.4-2026-03-05`. Overrides are `exec env`-scoped so a sibling `csk` shell is untouched.
- Created `~/.osk-litellm.yaml`: maps `gpt-5.4-2026-03-05` plus `claude-sonnet-4-6`, `claude-opus-4-7`, `claude-haiku-4-5-20251001` all to `openai/gpt-5.4-2026-03-05` (Claude Code's internal model picks route correctly). `drop_params: true` for max_tokens auto-mapping.
- OPENAI_API_KEY sourced from `~/.claude/env/shared.env` if missing in env. Note: `shared.env` uses bare `KEY=val` (no `export`) — the osk script uses inline `OPENAI_API_KEY="$OPENAI_API_KEY" cmd` form so child inherits it.
- LiteLLM bound to `127.0.0.1:4100` only (no LAN/Tailscale leak). Log: `~/.osk-litellm.log`. Singleton — multiple `osk` invocations share the proxy.
- Verified 2026-05-14: end-to-end `POST /v1/messages` with `gpt-5.4-2026-03-05` → "PONG", `claude-sonnet-4-6` alias → "OK". HTTP 200. LiteLLM 1.83.14, claude 2.1.126.
- Overrides: `OSK_MODEL`, `OSK_PORT`, `OSK_CONFIG`, `OSK_LOG` env vars.
- **Removed `master_key: sk-osk-local` from `~/.osk-litellm.yaml` (2026-05-14)** — Claude Code 2.1.126's auth header didn't exactly match the master_key string, so LiteLLM fell into the virtual-key DB lookup branch and returned `400 No connected db` (see `litellm/proxy/auth/user_api_key_auth.py:1156-1166`). With `master_key` omitted, the `master_key is None` branch at line 922 accepts any key without DB lookup. Safe because proxy binds 127.0.0.1 only. Do NOT re-introduce `master_key` here — `/health/liveliness` will still say "I'm alive!" but `/v1/messages` will 400 silently in the osk TUI.
- Open: no systemd unit (manual cleanup via `pkill -f "litellm --config.*osk-litellm"`); cost tracking via LiteLLM dashboard not configured.

## Current State (2026-05-11)

### LT-1 Crash Fix (2026-05-11)
- Crash: 0x9F DRIVER_POWER_STATE_FAILURE on S4 hibernate (May 7) — BugcheckCode=0x9F, SleepInProgress=4
- Fix 1: Fast Startup disabled (`HiberbootEnabled=0` in registry)
- Fix 2: Nahimic (4 services) stopped + disabled — NahimicService, NahimicBTLink, NahimicXVAD, Nahimic_Mirroring
- Fix 3: NVIDIA driver updated 577.05 → 596.36 (RTX 5070 Laptop)
- ClaudeNotifyListener: Running ✅ (AtStartup trigger holding)

## Current State (2026-05-06)

### SSH / Connectivity
- WSL2 sshd: ClientAliveInterval=60, ClientAliveCountMax=10 (was 10/6 — fixed VS Code reconnect loop)
- WSL2 → LT-1: `ssh lt-1` works ✅ (100.125.152.31, be2ja, id_ed25519)
- WSL2 → LT-3: `ssh lt-3` works ✅ (100.110.117.8, be2ja)
- LT-1 → WSL2: `ssh home-wsl` works ✅ (id_home_wsl_lt-1, User desk-1)
- LT-3 → WSL2: `ssh home-wsl` works ✅
- authorized_keys: 5 keys — `#ssh.id @be2jay` (mobile), `lt-1`, `lt-3`, `desk-1` (Win host→WSL2), `ipad` (iPad Pro, added 2026-05-07)
- Bootstrap: idempotent (delete-first-then-recreate for task/ACL/firewall), both LT-1 + LT-3 bootstrapped ✅

### GDrive Backup (2026-05-02)
- rclone installed: `~/.local/bin/rclone`, OAuth2 gdrive: remote (be2jay67@gmail.com)
- Filtered backup: FromScratch + HugwartsBanana + CTX → `gdrive:claude-backups/vault-filtered.db` (138MB)
- GDrive public share REVOKED (was: 1YPByRpNhd-Q2hGM2BD3QJk3MaOLVfTU3) — now private
- Triggers: Stop hook (async) + systemd timer every 6h
- Script: `~/.local/bin/backup-vault-filtered-gdrive.sh` (add projects via PROJECTS list)

### Security Fixes Applied (2026-05-06)
- LT-1 BitLocker: ON, Fully Encrypted ✅ (confirmed)
- LT-1 Secure Boot: ON ✅ (confirmed)
- LT-1 Kernel DMA Guard: DeviceEnumerationPolicy=1 set via reg.exe ✅ (blocks Thunderbolt DMA on locked screen)
- Win+L safe for short absences; shutdown/hibernate recommended for overnight/travel
- CRD (desk-1 Windows host): FULLY REMOVED ✅ — chromoting service, firewall rules, MSI, registry keys all deleted; Google-side auth revoked at remotedesktop.google.com/access

### Security Fixes Applied (2026-05-13)
- hub.service (port 9000 uvicorn): rebound `0.0.0.0` → `100.119.82.4` (Tailscale only) — matches pattern of 9955 fix
- hub.service refactored to `EnvironmentFile=~/.config/hub/env` for PyPI distribution readiness
- WSL2 autostart: `wsl2-autostart.vbs` added to Windows Startup folder — boots Ubuntu silently at logon (no admin needed)
- Distribution rule: hub ships with `HUB_HOST=127.0.0.1` default; `hub setup` detects Tailscale IP via `tailscale ip -4` and writes to `~/.config/hub/env`

### DESK-1 Notify Listener Restored (2026-05-13)
- Root cause: LT-1's `~/.ssh/config` had `RemoteForward 6789 127.0.0.1:6789` → SSH tunnel held WSL2's `127.0.0.1:6789` → `wslrelay` mirrored to DESK-1 Windows-side `127.0.0.1:6789` → DESK-1's `claude-notify-listener.ps1` failed to bind `http://+:6789/` (URL ACL conflict, "다른 등록과 충돌")
- Fix: stripped `RemoteForward 6789` from LT-1 `~/.ssh/config` (backup: `.bak-20260513172346`), killed active LT-1 SSH session, started listener via `Start-Process` (HTTP.SYS PID 4 owns the port now)
- Persistence: `claude-notify-listener.vbs` in `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\` (no admin/UAC needed; ScheduledTask `/RL HIGHEST` would need elevation)
- Patched `client-setup-ps5.ps1` line 446: removed `RemoteForward 6789 127.0.0.1:6789` from the `home-wsl` SSH config template (was contradicting line 2 docstring "no SSH tunnel"). Bootstrap server serves patched version immediately (no restart needed — SimpleHTTPRequestHandler reads on demand)
- ps5 line 450 regex strips the old `Host home-wsl` block before writing — so any future re-bootstrap on a client automatically cleans the stale `RemoteForward` line
- Verified: `curl 100.115.17.46:6789/notify` → 200, `curl 100.125.152.31:6789/notify` → 200, WSL2 `:6789` empty (no tunnel)

### WSL2 Session Persistence Across VS Code Close (2026-05-13, M5)
- `C:\Users\DESK-1\.wslconfig` created with `[wsl2] vmIdleTimeout=-1` — disables default 60s auto-shutdown when no clients connected. Setting applies on next WSL boot (no `wsl --shutdown` forced; current sessions preserved).
- Verified: all zellij servers + tmux session-servers are PPID=1 (reparented to init), so they survive any VS Code/SSH client disconnect. 14 sessions confirmed detached: 8 zellij (`SVTool-*`, `VERTICAL-*`) + 6 tmux (`claude-exec-*`).
- Net effect: closing the VS Code WSL window no longer risks killing background work. VS Code Server itself (PID 875 node) lingers ~3 min after disconnect then shuts down; auto-restarts on reconnect.

### LT-1 Windows Update Reboot Hardening (2026-05-13, M3)
- `HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU`: `NoAutoRebootWithLoggedOnUsers=1`, `AlwaysAutoRebootAtScheduledTime=0` — blocks unattended reboot while session is active
- `HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate`: `SetActiveHours=1`, `ActiveHoursStart=6`, `ActiveHoursEnd=23`, `ActiveHoursMaxRange=18` (Win11 hard cap is 18h)
- `HKLM\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings\SmartActiveHoursState=0` — disables ML-driven override
- 35-day update pause set via `PausedFeatureStatus=1`/`PausedQualityStatus=1` (belt-and-suspenders, needs manual renewal)
- Note: legacy reboot scheduled tasks (`Reboot`, `Reboot_AC`, `Reboot_Battery`) ARE GONE on this Win11 build — reboot is now driven by `UsoSvc`/`MoUsoCoreWorker.exe`, controlled by the registry policy above. `UsoSvc` left running (required for security update scans). `USO_UxBroker` and `Schedule Wake To Work` are TrustedInstaller-owned, cannot disable without taking ownership — not needed since policy blocks the reboot itself.

### Security Fixes Applied (2026-05-02 evening)
- VNC x11vnc: added `-localhost` flag → ports now `[::1]` loopback only (was `[::]` all interfaces)
- Bootstrap 9955: rebound `0.0.0.0` → `100.119.82.4` (Tailscale only, token no longer leaks to LAN)
- CTX http server 8788: killed (was serving CTX docs to 0.0.0.0)
- Docker ctx-dashboard 8787: rebound `0.0.0.0` → `127.0.0.1`
- HugwartsBanana package.json dev script: patched `-H 127.0.0.1` (takes effect on next restart)
- Remaining: Next.js 3000 still on `*:3000` for current run — kill when convenient

### Security Fixes Applied (2026-05-02)
- `/register-key` restricted to localhost only (tailnet peers blocked)
- Notify listener token auth: `/expose`, `/clipboard`, `/unexpose` require `X-Notify-Token` header
- Shared secret: `~/.claude/.notify-secret` (injected into PS1 at bootstrap serve time)
- All WSL2 hooks updated with token: windows-notify.sh, windows-stop.sh, close-popup.sh, wsl-expose, wsl-unexpose
- vault-filtered.db GDrive public share revoked
- rclone.conf chmod 600

### Security Fixes Applied (2026-05-01)
- playwright-mcp-novnc: all services bound to 127.0.0.1 (was 0.0.0.0)
- WSL2 private key permissions fixed: DCTN×3, aether-b200-v28-1, id_container_nipa×2 → 600
- id_ed25519.compromised.bak → chmod 000 (locked, not in any authorized_keys)
- CRD on LT-1: zero new inbound ports confirmed (CRD since fully removed from desk-1 Win host)

### Syncthing — REMOVED (2026-05-05)
- WSL2: systemd service stopped+disabled, binary+config deleted (`~/.local/bin/syncthing`, `~/.config/syncthing/`)
- LT-3: config folder removed (`C:\Users\be2ja\AppData\Local\syncthing`), no binary found
- LT-1: confirmed clean — no Syncthing ever installed
- `~/claude-inbox/` folder remains on WSL2 (contents, not Syncthing)

### Open Items
- LT-1 known_hosts: stale ssh-rsa entry for 100.119.82.4 (cosmetic)
- LT-1 sshd_config comment: packetanal@wsl2-new → wsl2-to-lt1 (needs elevated PS on LT-1)
- id_container / id_container_nipa_* are RSA-2048 — replace with ed25519 on next NIPA rotation
