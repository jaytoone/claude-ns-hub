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
