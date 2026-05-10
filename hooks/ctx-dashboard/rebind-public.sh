#!/usr/bin/env bash
# Rebind CTX dashboard from 127.0.0.1 → 0.0.0.0 so it's reachable on tailnet.
# Assumes Tailscale is already up on WSL (but doesn't require it — just binds public).
# Idempotent: stop if running, restart with new bind.

set -e
HERE="$HOME/.claude/hooks/ctx-dashboard"
PIDFILE="/tmp/ctx-dashboard.pid"
PORT="${CTX_DASHBOARD_PORT:-8787}"

# ── stop current instance if any ──────────────────────────────────
if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
  kill "$(cat "$PIDFILE")" || true
  sleep 1
fi

# ── start bound to 0.0.0.0 ────────────────────────────────────────
CTX_DASHBOARD_HOST=0.0.0.0 bash "$HERE/launch.sh" "$PORT"
sleep 2

# ── verify ────────────────────────────────────────────────────────
if curl -sf "http://127.0.0.1:$PORT/" -o /dev/null; then
  echo "✓ Dashboard responding (bound to 0.0.0.0:$PORT)"
else
  echo "✗ Not responding — check /tmp/ctx-dashboard.log" >&2
  exit 1
fi

# ── print reach URLs if Tailscale is up ───────────────────────────
if command -v tailscale >/dev/null 2>&1; then
  IP=$(tailscale ip -4 2>/dev/null | head -1)
  DNS=$(tailscale status --json 2>/dev/null | python3 -c "import sys,json; print(json.loads(sys.stdin.read())['Self']['DNSName'].rstrip('.'))" 2>/dev/null || echo "")
  if [[ -n "$IP" ]]; then
    echo ""
    echo "  Reach from tailnet:"
    [[ -n "$DNS" ]] && echo "    http://$DNS:$PORT/"
    echo "    http://$IP:$PORT/"
  fi
fi
