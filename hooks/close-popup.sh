#!/bin/bash
# 현재 프로젝트의 모든 팝업을 sentinel로 자동 종료
LOCK_DIR="/tmp/claude-notify-stack"
input=$(cat 2>/dev/null)
transcript_path=$(echo "$input" | jq -r '.transcript_path // empty' 2>/dev/null)
if [ -n "$transcript_path" ]; then
    proj_key=$(basename "$(dirname "$transcript_path")")
else
    current_path=$(echo "$input" | jq -r '.cwd // empty' 2>/dev/null)
    [ -z "$current_path" ] && current_path="$(pwd)"
    proj_key=$(basename "$current_path")
fi

# Local slot sentinels (only applies when WinForms runs locally — REMOTE_NOTIFY_ONLY=0)
if [ -d "$LOCK_DIR" ]; then
    for d in "$LOCK_DIR"/slot_*/; do
        proj_file="$d/proj"
        if [ -f "$proj_file" ] && [ "$(cat "$proj_file" 2>/dev/null)" = "$proj_key" ]; then
            touch "$d/close"
        fi
    done
fi

# Remote close (SSH reverse-tunnel to env #1 listener) — fires when CLAUDE_REMOTE_NOTIFY_URL is set.
# IMPORTANT: the remote listener derives proj_key from the notify TITLE (basename of cwd),
# NOT from transcript_path hash. So we must send the cwd-basename here, even when
# transcript_path was used for the local slot matching above.
if [ -n "${CLAUDE_REMOTE_NOTIFY_URL:-}" ]; then
    remote_current_path=$(echo "$input" | jq -r '.cwd // empty' 2>/dev/null)
    [ -z "$remote_current_path" ] && remote_current_path="$(pwd)"
    remote_proj_key=$(basename "$remote_current_path")
    if [ -n "$remote_proj_key" ]; then
        (
            payload=$(jq -cn --arg k "$remote_proj_key" '{proj_key:$k}')
            # Tailscale direct: enumerate online Windows peers, POST to each on port 6789
            tailscale status --json 2>/dev/null | \
                jq -r '.Peer[] | select(.Online==true and (.OS=="windows")) | .TailscaleIPs[0]' 2>/dev/null | \
                while read -r ip; do
                    [ -n "$ip" ] && curl -sf -m 2 -X POST "http://${ip}:6789/close" \
                         -H 'Content-Type: application/json' \
                         --data "$payload" >/dev/null 2>&1 || true
                done
        ) </dev/null &
        disown 2>/dev/null || true
    fi
fi

exit 0
