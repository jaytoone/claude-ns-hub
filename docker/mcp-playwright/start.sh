#!/bin/bash
# Start virtual display
Xvfb :1 -screen 0 1280x800x24 &
sleep 1

# Start VNC server (no password)
x11vnc -display :1 -nopw -listen 0.0.0.0 -xkb -forever -rfbport 5901 &
sleep 1

# Start noVNC websocket proxy
websockify --web /usr/share/novnc 6901 localhost:5901 &
sleep 1

# Start playwright MCP in headed mode (visible in VNC)
NODE=$(which node)
CLI=$(npm root -g)/@playwright/mcp/cli.js
exec "$NODE" "$CLI" --port 8831 --browser chromium --args="--no-sandbox,--disable-setuid-sandbox"
