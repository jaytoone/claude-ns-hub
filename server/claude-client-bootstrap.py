#!/usr/bin/env python3
"""Claude client bootstrap server — serves client-setup-ps5.ps1 via Tailscale.

One-line client onboarding: irm http://<tailscale-ip>:9955/bootstrap | iex

Endpoints:
  GET /bootstrap   → dynamic PS1 that downloads and runs client-setup-ps5.ps1
  GET /<file>      → static file from ~/.claude/hooks/ (%%WSL2_TAILSCALE_IP%% substituted)

Architecture: all clients bind port 6789 (their own Tailscale IP); WSL2 hooks
enumerate tailnet peers and POST directly (no SSH tunnel, no port allocation).
Spec 3 (browser tunnel) via listener /expose endpoint + wsl-expose <port> CLI.
Spec 4 (noVNC) via novnc/wsl-novnc-start — exposes ports 6901+8831.
"""
import subprocess
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

HOOKS_DIR = Path.home() / ".claude" / "hooks"
SERVER_PORT = 9955


def get_tailscale_ip() -> str:
    try:
        return subprocess.check_output(["tailscale", "ip", "--1"], text=True).strip()
    except Exception:
        return "127.0.0.1"


SERVER_TAILSCALE_IP = get_tailscale_ip()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(HOOKS_DIR), **kwargs)

    def log_message(self, fmt, *args):
        import sys
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _text(self, body, status=200, ctype="text/plain; charset=utf-8"):
        data = body.encode() if isinstance(body, str) else body
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/bootstrap":
            script = f"""# Claude client bootstrap — Tailscale direct POST (common port 6789)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'  # avoid ReadConsoleOutput error over SSH
$f = Join-Path $env:TEMP 'cs.ps1'
Invoke-WebRequest "http://{SERVER_TAILSCALE_IP}:{SERVER_PORT}/client-setup-ps5.ps1" -OutFile $f -UseBasicParsing | Out-Null
& powershell.exe -ExecutionPolicy Bypass -File $f
"""
            self._text(script)
            return

        # For client-setup-ps5.ps1: inject current Tailscale IP into portproxy connectaddress
        if parsed.path.lstrip("/") == "client-setup-ps5.ps1":
            ps1_path = HOOKS_DIR / "client-setup-ps5.ps1"
            if ps1_path.exists():
                content = ps1_path.read_text(encoding="utf-8")
                content = content.replace("%%WSL2_TAILSCALE_IP%%", SERVER_TAILSCALE_IP)
                self._text(content, ctype="text/plain; charset=utf-8")
                return

        super().do_GET()


def main():
    server = HTTPServer(("0.0.0.0", SERVER_PORT), Handler)
    print(f"Claude client bootstrap on 0.0.0.0:{SERVER_PORT} (tailscale: {SERVER_TAILSCALE_IP})")
    print(f"  Onboarding URL: irm http://{SERVER_TAILSCALE_IP}:{SERVER_PORT}/bootstrap | iex")
    server.serve_forever()


if __name__ == "__main__":
    main()
