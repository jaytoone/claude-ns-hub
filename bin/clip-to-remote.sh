#!/bin/bash
# Fire-and-forget clipboard POST to all online Windows tailnet clients.
# Called by zellij copy_command — reads stdin, returns immediately, POST happens in background.
tmp=$(mktemp)
cat > "$tmp"
(
    # Tailscale direct: enumerate online Windows peers, POST to each on port 6789
    tailscale status --json 2>/dev/null | \
        jq -r '.Peer[] | select(.Online==true and (.OS=="windows")) | .TailscaleIPs[0]' 2>/dev/null | \
        while read -r ip; do
            [ -n "$ip" ] && curl -sf -m 3 -X POST --data-binary @"$tmp" \
                 "http://${ip}:6789/clipboard" >/dev/null 2>&1 || true
        done
    rm -f "$tmp"
) </dev/null >/dev/null 2>&1 &
disown 2>/dev/null || true
exit 0
