#!/usr/bin/env bash
# Start a headless Chrome with CDP exposed on localhost:9222.
# MCP server `playwright-cdp` attaches to this via --cdp-endpoint.
# VS Code Remote-SSH auto-forwards 9222; on env #1 open chrome://inspect to attach.
#
# Usage:
#   ~/.claude/snippets/pw-cdp-start.sh           # starts in background, logs to /tmp/pw-cdp.log
#   ~/.claude/snippets/pw-cdp-start.sh --fg      # foreground
#   ~/.claude/snippets/pw-cdp-start.sh --stop    # stop running instance
#   PORT=9333 ~/.claude/snippets/pw-cdp-start.sh # custom port
set -euo pipefail

PORT="${PORT:-9222}"
USER_DATA="${USER_DATA:-$HOME/.playwright-sessions/cdp}"
PIDFILE="/tmp/pw-cdp-${PORT}.pid"
LOGFILE="/tmp/pw-cdp-${PORT}.log"

CHROME=""
for cand in \
    "$HOME/.cache/ms-playwright/chromium-1217/chrome-linux64/chrome" \
    "$HOME/.cache/ms-playwright/chromium-1208/chrome-linux64/chrome" \
    "/usr/bin/google-chrome" \
    "/usr/bin/chromium" \
    "/usr/bin/chromium-browser"; do
    if [ -x "$cand" ]; then CHROME="$cand"; break; fi
done
[ -n "$CHROME" ] || { echo "ERROR: no chrome/chromium binary found" >&2; exit 1; }

stop() {
    if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
        kill "$(cat "$PIDFILE")" && echo "stopped pid $(cat "$PIDFILE")"
        rm -f "$PIDFILE"
    else
        echo "not running"
    fi
}

case "${1:-}" in
    --stop) stop; exit 0 ;;
esac

if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    echo "already running (pid $(cat "$PIDFILE"), port $PORT)"
    exit 0
fi

mkdir -p "$USER_DATA"

ARGS=(
    --remote-debugging-port="$PORT"
    --remote-debugging-address=127.0.0.1
    --user-data-dir="$USER_DATA"
    --headless=new
    --disable-gpu
    --no-first-run
    --no-default-browser-check
    --disable-dev-shm-usage
)

if [ "${1:-}" = "--fg" ]; then
    echo "chrome: $CHROME"
    echo "port:   $PORT"
    echo "data:   $USER_DATA"
    exec "$CHROME" "${ARGS[@]}"
fi

nohup "$CHROME" "${ARGS[@]}" >"$LOGFILE" 2>&1 &
echo $! > "$PIDFILE"
sleep 0.5
echo "started pid $(cat "$PIDFILE") on http://localhost:${PORT}  (log: $LOGFILE)"
echo "attach from env #1: open chrome://inspect → Configure → add localhost:${PORT}"
