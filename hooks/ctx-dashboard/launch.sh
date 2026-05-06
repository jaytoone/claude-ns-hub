#!/usr/bin/env bash
# Launch the CTX dashboard server (idempotent) and open it in the default browser.
# Usage: ctx            # port 8787
#        ctx 9000       # custom port

set -euo pipefail

PORT="${1:-${CTX_DASHBOARD_PORT:-8787}}"
HERE="$HOME/.claude/hooks/ctx-dashboard"
PIDFILE="/tmp/ctx-dashboard.pid"
LOG="/tmp/ctx-dashboard.log"

_tailscale_ip() {
  # Prefer the bindable tailscale0 IP (from ip addr); fall back to 127.0.0.1
  ip addr show tailscale0 2>/dev/null \
    | awk '/inet / {split($2,a,"/"); print a[1]; exit}' \
    || echo "127.0.0.1"
}

start_server() {
  local _host="${CTX_DASHBOARD_HOST:-$(_tailscale_ip)}"
  CTX_DASHBOARD_PORT="$PORT" \
  CTX_DASHBOARD_HOST="$_host" \
  nohup python3 "$HERE/server.py" > "$LOG" 2>&1 &
  echo $! > "$PIDFILE"
  sleep 1
}

is_our_server() {
  # Return 0 if the process listening on $PORT is a ctx-dashboard server.
  # `ps args` only shows `python3 server.py` when launched via `cd dir && python3 server.py`,
  # so we also check /proc/$PID/cwd (Linux) which points to the invocation directory.
  local listen_pid cmd cwd_link
  listen_pid=$(lsof -iTCP:"$PORT" -sTCP:LISTEN -t 2>/dev/null | head -1)
  [[ -z "$listen_pid" ]] && return 1
  cmd=$(ps -p "$listen_pid" -o args= 2>/dev/null)
  [[ "$cmd" == *"ctx-dashboard/server.py"* ]] && return 0
  # Fallback: does its cwd live under ctx-dashboard/ AND is it running server.py?
  cwd_link=$(readlink "/proc/$listen_pid/cwd" 2>/dev/null)
  if [[ "$cwd_link" == *"/ctx-dashboard"* ]] && [[ "$cmd" == *"server.py"* ]]; then
    return 0
  fi
  return 1
}

# If a pidfile exists and the process is alive, reuse it
if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
  EXISTING_PID="$(cat "$PIDFILE")"
  if lsof -Pan -p "$EXISTING_PID" -iTCP -sTCP:LISTEN 2>/dev/null | grep -q ":$PORT"; then
    echo "CTX Dashboard already running (pid $EXISTING_PID) → http://127.0.0.1:$PORT"
  else
    echo "Stale pidfile — restarting…"
    kill "$EXISTING_PID" 2>/dev/null || true
    rm -f "$PIDFILE"
    start_server
    echo "CTX Dashboard → http://127.0.0.1:$PORT"
  fi
elif is_our_server; then
  # Server is running from a previous session with no pidfile — adopt it
  EXISTING_PID=$(lsof -iTCP:"$PORT" -sTCP:LISTEN -t 2>/dev/null | head -1)
  echo "$EXISTING_PID" > "$PIDFILE"
  echo "CTX Dashboard already running (pid $EXISTING_PID, adopted) → http://127.0.0.1:$PORT"
else
  # Check if port is already LISTENING by something that is NOT our server
  if lsof -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
    echo "Port $PORT is in use by another process. Pick a different port: ctx <port>"
    exit 1
  fi
  start_server
  echo "CTX Dashboard → http://127.0.0.1:$PORT"
fi

# Try to open browser (best-effort, no error if headless)
_BIND_HOST=$(grep "CTX Dashboard →" "$LOG" 2>/dev/null | tail -1 | sed 's|.*http://||;s|:.*||')
URL="http://${_BIND_HOST:-127.0.0.1}:$PORT"
WSL_EXPLORER="/mnt/c/Windows/explorer.exe"
if command -v wslview    >/dev/null 2>&1; then wslview    "$URL" >/dev/null 2>&1 || true
elif [[ -x "$WSL_EXPLORER" ]];              then "$WSL_EXPLORER" "$URL" >/dev/null 2>&1 || true
elif command -v xdg-open >/dev/null 2>&1; then xdg-open "$URL" >/dev/null 2>&1 || true
elif command -v open       >/dev/null 2>&1; then open       "$URL" >/dev/null 2>&1 || true
fi

echo "Logs: $LOG    Stop: ctx-stop   (or: kill \$(cat $PIDFILE))"
