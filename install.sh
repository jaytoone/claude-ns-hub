#!/bin/bash
# install.sh — restore Claude client bootstrap on a fresh WSL2 instance.
# Usage: bash install.sh   (run from repo root after git clone)
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOKS_DIR="$HOME/.claude/hooks"
BIN_DIR="$HOME/.local/bin"
SYSTEMD_DIR="$HOME/.config/systemd/user"

echo "=== Claude Client Bootstrap — WSL2 Server Install ==="
echo ""

# Prerequisites check
ok=1
command -v tailscale &>/dev/null || { echo "WARNING: tailscale not on PATH — IP auto-detection needs it running"; ok=0; }
command -v jq &>/dev/null || { echo "WARNING: jq not found (needed by hooks) — install: sudo apt install jq"; ok=0; }
command -v docker &>/dev/null || {
    echo "WARNING: docker not found — Spec 4 (noVNC) requires Docker Desktop + WSL2 integration"
    echo "  Docker Desktop → Settings → Resources → WSL Integration → enable your distro"
    ok=0
}
[ "$ok" -eq 0 ] && echo ""

# 1. Server + hooks
mkdir -p "$HOOKS_DIR"
cp "$REPO_DIR/server/claude-client-bootstrap.py" "$HOOKS_DIR/"
cp "$REPO_DIR/hooks/windows-notify.sh" "$HOOKS_DIR/"
cp "$REPO_DIR/hooks/windows-stop.sh" "$HOOKS_DIR/"
cp "$REPO_DIR/hooks/close-popup.sh" "$HOOKS_DIR/"
cp "$REPO_DIR/client/client-setup-ps5.ps1" "$HOOKS_DIR/"
chmod +x "$HOOKS_DIR/windows-notify.sh" "$HOOKS_DIR/windows-stop.sh" "$HOOKS_DIR/close-popup.sh"
echo "[1/4] Hooks + server copied to $HOOKS_DIR"

# 2. CLI tools
mkdir -p "$BIN_DIR"
cp "$REPO_DIR/bin/wsl-expose" "$BIN_DIR/"
cp "$REPO_DIR/bin/wsl-unexpose" "$BIN_DIR/"
cp "$REPO_DIR/bin/clip-to-remote.sh" "$BIN_DIR/"
chmod +x "$BIN_DIR/wsl-expose" "$BIN_DIR/wsl-unexpose" "$BIN_DIR/clip-to-remote.sh"
echo "[2/4] CLI tools installed to $BIN_DIR"

# 3. Systemd service
mkdir -p "$SYSTEMD_DIR"
cp "$REPO_DIR/server/claude-client-bootstrap.service" "$SYSTEMD_DIR/"
systemctl --user daemon-reload
systemctl --user enable claude-client-bootstrap
systemctl --user restart claude-client-bootstrap
echo "[3/4] Systemd service enabled + started"

# 4. Health check
sleep 2
TAILSCALE_IP=$(tailscale ip --1 2>/dev/null || echo "your-tailscale-ip")
if curl -sf "http://localhost:9955/bootstrap" >/dev/null 2>&1; then
    echo "[4/4] Server healthy"
    echo ""
    echo "=== DONE ==="
    echo ""
    echo "Windows onboarding (run in admin PowerShell on any tailnet PC):"
    echo "  irm http://${TAILSCALE_IP}:9955/bootstrap | iex"
    echo ""
    echo "noVNC (Spec 4 — Playwright browser):"
    echo "  $REPO_DIR/novnc/wsl-novnc-start"
else
    echo "[4/4] Server not responding — check logs:"
    echo "  systemctl --user status claude-client-bootstrap"
    echo "  journalctl --user -u claude-client-bootstrap -n 20"
fi
