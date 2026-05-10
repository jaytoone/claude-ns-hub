#!/usr/bin/env python3
"""
Tiny HTTP → OS-native notification bridge.

Runs on the CLIENT PC that you're VS Code Remote-SSHing from.
The WSL2 host pushes notifications over the existing SSH connection
(reverse tunnel: ssh -R 6789:localhost:6789 ...), so curl hitting
localhost:6789 on the WSL2 side emerges on the client's loopback
and this script pops a native toast.

Stdlib only. Tested on macOS, Linux (notify-send), Windows 10/11.

Usage on client:
    python3 notify-listener.py                 # binds 127.0.0.1:6789
    python3 notify-listener.py --port 6800     # custom port
    python3 notify-listener.py --host 0.0.0.0  # listen on LAN (careful)

Then in ~/.ssh/config on the client:
    Host your-wsl-host
        RemoteForward 6789 localhost:6789

VS Code Remote-SSH reads ssh_config, so the tunnel activates
automatically every time you connect.
"""

import argparse
import json
import platform
import shlex
import shutil
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

SYS = platform.system()


def _run_bg(cmd, timeout=None):
    try:
        if timeout is None:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.run(cmd, timeout=timeout, check=False,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as exc:
        print(f"[notify] launch failed: {exc}", file=sys.stderr)


def notify(title, message, sound=True):
    title = (title or "Claude").strip() or "Claude"
    message = (message or "").strip()

    if SYS == "Darwin":
        script = (
            f'display notification {json.dumps(message)} '
            f'with title {json.dumps(title)}'
        )
        if sound:
            script += ' sound name "Ping"'
        _run_bg(["osascript", "-e", script])
        return

    if SYS == "Linux":
        if shutil.which("notify-send"):
            _run_bg(["notify-send", "--app-name=Claude", "--", title, message])
        elif shutil.which("zenity"):
            _run_bg(["zenity", "--notification", f"--text={title}: {message}"])
        else:
            print(f"[notify] {title}: {message}")
        return

    if SYS == "Windows":
        t = title.replace("'", "''")
        m = message.replace("'", "''")
        ps = (
            "[System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms') | Out-Null;"
            "[System.Reflection.Assembly]::LoadWithPartialName('System.Drawing') | Out-Null;"
            "$ni = New-Object System.Windows.Forms.NotifyIcon;"
            "$ni.Icon = [System.Drawing.SystemIcons]::Information;"
            f"$ni.BalloonTipTitle = '{t}';"
            f"$ni.BalloonTipText  = '{m}';"
            "$ni.Visible = $true;"
            "$ni.ShowBalloonTip(4000);"
            "Start-Sleep -Milliseconds 4500;"
            "$ni.Dispose()"
        )
        _run_bg(["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps])
        return

    print(f"[notify] {title}: {message}")


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body=b"ok"):
        self.send_response(code)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/health"):
            self._send(200, b"ok")
        else:
            self._send(404, b"not found")

    def do_POST(self):
        if self.path != "/notify":
            self._send(404, b"not found")
            return
        n = int(self.headers.get("Content-Length", 0) or 0)
        raw = self.rfile.read(n).decode("utf-8", "replace") if n else ""
        try:
            data = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            data = {"title": "Claude", "message": raw}
        notify(
            data.get("title") or "Claude",
            data.get("message") or "",
            bool(data.get("sound", True)),
        )
        self._send(200, b"ok")

    def log_message(self, *args, **kwargs):
        return  # silence access log


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=6789)
    args = ap.parse_args()
    srv = HTTPServer((args.host, args.port), Handler)
    print(f"[notify] listening on {args.host}:{args.port} ({SYS})")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
