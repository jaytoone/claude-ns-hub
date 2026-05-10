# client-setup.ps1 - one-shot Windows client installer for Claude remote notify
# Run once from PowerShell on the CLIENT PC (desktop-693ueou):
#   scp -P 2222 jayone@100.69.161.128:~/.claude/hooks/client-setup.ps1 $env:TEMP\s.ps1
#   powershell -NoProfile -ExecutionPolicy Bypass -File $env:TEMP\s.ps1
#
# What it does (all idempotent, all reversible):
#   1. Writes ~\claude-notify-listener.py (embedded, ~130 lines)
#   2. Ensures Python 3 exists (bails with guidance if not)
#   3. Registers a Task Scheduler "ClaudeNotifyListener" at user login
#   4. Starts the listener now
#   5. Adds "RemoteForward 6789 localhost:6789" to ~\.ssh\config for host
#      100.69.161.128 (your WSL2 jump) if not already there
#   6. Self-tests by POSTing to localhost:6789/notify

$ErrorActionPreference = "Stop"
$HomeDir = $env:USERPROFILE
$ListenerPath = Join-Path $HomeDir "claude-notify-listener.py"
$SshConfig = Join-Path $HomeDir ".ssh\config"
$TaskName = "ClaudeNotifyListener"

# ---------- 1. check Python ----------
$py = (Get-Command python -ErrorAction SilentlyContinue) ??
      (Get-Command python3 -ErrorAction SilentlyContinue) ??
      (Get-Command py -ErrorAction SilentlyContinue)
if (-not $py) {
    Write-Host "`n[!] Python 3 not found. Install from https://www.python.org/downloads/ (check 'Add to PATH'), then rerun this script." -ForegroundColor Red
    exit 1
}
$pyExe = $py.Source
Write-Host "[ok] python: $pyExe" -ForegroundColor Green

# ---------- 2. write listener ----------
$listener = @'
#!/usr/bin/env python3
"""HTTP -> OS-native notification bridge (stdlib only)."""
import argparse, json, platform, shutil, subprocess, sys
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
        script = f'display notification {json.dumps(message)} with title {json.dumps(title)}'
        if sound: script += ' sound name "Ping"'
        _run_bg(["osascript", "-e", script]); return
    if SYS == "Linux":
        if shutil.which("notify-send"):
            _run_bg(["notify-send", "--app-name=Claude", "--", title, message])
        else:
            print(f"[notify] {title}: {message}")
        return
    if SYS == "Windows":
        t = title.replace("'", "''"); m = message.replace("'", "''")
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
        _run_bg(["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps]); return
    print(f"[notify] {title}: {message}")

class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body=b"ok"):
        self.send_response(code)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        if self.path in ("/", "/health"): self._send(200, b"ok")
        else: self._send(404, b"not found")
    def do_POST(self):
        if self.path != "/notify": self._send(404, b"not found"); return
        n = int(self.headers.get("Content-Length", 0) or 0)
        raw = self.rfile.read(n).decode("utf-8", "replace") if n else ""
        try: data = json.loads(raw) if raw else {}
        except json.JSONDecodeError: data = {"title": "Claude", "message": raw}
        notify(data.get("title") or "Claude", data.get("message") or "", bool(data.get("sound", True)))
        self._send(200, b"ok")
    def log_message(self, *a, **k): return

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=6789)
    args = ap.parse_args()
    srv = HTTPServer((args.host, args.port), Handler)
    print(f"[notify] listening on {args.host}:{args.port} ({SYS})", flush=True)
    try: srv.serve_forever()
    except KeyboardInterrupt: pass

if __name__ == "__main__":
    main()
'@

$listener | Out-File -FilePath $ListenerPath -Encoding UTF8 -Force
Write-Host "[ok] wrote $ListenerPath" -ForegroundColor Green

# ---------- 3. Task Scheduler autostart ----------
$action   = New-ScheduledTaskAction -Execute $pyExe -Argument "`"$ListenerPath`""
$trigger  = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -Hidden
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Force | Out-Null
Write-Host "[ok] task scheduled: $TaskName (runs at logon)" -ForegroundColor Green

# ---------- 4. start now (background) ----------
Start-Process -FilePath $pyExe -ArgumentList "`"$ListenerPath`"" -WindowStyle Hidden
Start-Sleep -Seconds 1

# ---------- 5. ensure ssh_config has RemoteForward ----------
$sshDir = Split-Path $SshConfig -Parent
if (-not (Test-Path $sshDir)) { New-Item -ItemType Directory -Path $sshDir -Force | Out-Null }
if (-not (Test-Path $SshConfig)) { New-Item -ItemType File -Path $SshConfig -Force | Out-Null }
$cfg = Get-Content $SshConfig -Raw -ErrorAction SilentlyContinue
if ($cfg -notmatch 'RemoteForward\s+6789\s+localhost:6789') {
    $block = @"

# --- Claude remote notify (added by client-setup.ps1 on $(Get-Date -Format 'yyyy-MM-dd')) ---
Host 100.69.161.128 desktop-8hiuju8 wsl-notify
    HostName 100.69.161.128
    Port 2222
    User jayone
    RemoteForward 6789 localhost:6789
    ServerAliveInterval 30
    ServerAliveCountMax 3
"@
    Add-Content -Path $SshConfig -Value $block
    Write-Host "[ok] appended RemoteForward block to $SshConfig" -ForegroundColor Green
} else {
    Write-Host "[skip] RemoteForward already present in $SshConfig" -ForegroundColor Yellow
}

# ---------- 6. self-test ----------
try {
    $resp = Invoke-WebRequest -Uri "http://localhost:6789/health" -UseBasicParsing -TimeoutSec 3
    if ($resp.StatusCode -eq 200) { Write-Host "[ok] listener healthy" -ForegroundColor Green }
    Invoke-WebRequest -Uri "http://localhost:6789/notify" -Method POST `
        -Body '{"title":"Claude","message":"setup complete"}' -ContentType "application/json" -UseBasicParsing -TimeoutSec 3 | Out-Null
    Write-Host "[ok] test toast fired - you should see a balloon now" -ForegroundColor Green
} catch {
    Write-Host "[warn] self-test failed: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "`n==== DONE ====`n" -ForegroundColor Cyan
Write-Host "Next: reconnect VS Code Remote-SSH (or any SSH session to the WSL2 host)."
Write-Host "The RemoteForward will activate automatically and Claude popups will"
Write-Host "appear on this PC as Windows balloon notifications."
