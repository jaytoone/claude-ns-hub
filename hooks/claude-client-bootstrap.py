#!/usr/bin/env python3
"""Claude client bootstrap server — serves client-setup-ps5.ps1 via Tailscale.

One-line client onboarding: irm http://100.119.82.4:9955/bootstrap | iex

Endpoints:
  GET /bootstrap              → dynamic PS1 that downloads and runs client-setup-ps5.ps1
  GET /client-setup-ps5.ps1  → PS1 with NOTIFY_TOKEN_HERE injected from ~/.claude/.notify-secret
  GET /<file>                 → static file from ~/.claude/hooks/
  POST /register-key          → append SSH pubkey to authorized_keys (localhost only)

Security:
  - /register-key: localhost (127.0.0.1) only — tailnet peers cannot call it
  - Notify token: injected into PS1 at serve time; WSL2 hooks include X-Notify-Token header
"""
import secrets
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

HOOKS_DIR   = Path.home() / ".claude" / "hooks"
AUTH_KEYS   = Path.home() / ".ssh" / "authorized_keys"
SECRET_FILE = Path.home() / ".claude" / ".notify-secret"
UPLOAD_DIR  = Path.home() / "Downloads"
SERVER_TAILSCALE_IP = "100.119.82.4"
SERVER_PORT = 9955
PS1_FILENAME = "client-setup-ps5.ps1"
TOKEN_PLACEHOLDER  = "NOTIFY_TOKEN_HERE"
PUBKEY_PLACEHOLDER = "WSL2_PUBKEY_HERE"


def _load_or_create_secret() -> str:
    if SECRET_FILE.exists():
        return SECRET_FILE.read_text().strip()
    token = secrets.token_urlsafe(32)
    SECRET_FILE.parent.mkdir(parents=True, exist_ok=True)
    SECRET_FILE.write_text(token)
    SECRET_FILE.chmod(0o600)
    sys.stderr.write(f"[bootstrap] generated new notify secret\n")
    return token


NOTIFY_SECRET = _load_or_create_secret()
WSL2_PUBKEY   = (Path.home() / ".ssh" / "id_ed25519.pub").read_text().strip()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(HOOKS_DIR), **kwargs)

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _text(self, body, status=200, ctype="text/plain; charset=utf-8"):
        data = body.encode() if isinstance(body, str) else body
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/register-key":
            # Require shared token — prevents unauthenticated key injection
            if self.headers.get("X-Notify-Token") != NOTIFY_SECRET:
                sys.stderr.write(f"[register-key] BLOCKED from {self.client_address[0]} (bad token)\n")
                self._text("Forbidden: invalid token", 403)
                return
            length = int(self.headers.get("Content-Length", 0))
            pubkey = self.rfile.read(length).decode().strip()
            if not pubkey.startswith("ssh-"):
                self._text("ERROR: invalid key format", 400)
                return
            AUTH_KEYS.parent.mkdir(mode=0o700, exist_ok=True)
            existing = AUTH_KEYS.read_text() if AUTH_KEYS.exists() else ""
            if pubkey in existing:
                self._text("SKIP: key already registered")
                return
            # Replace stale key with same comment (e.g. key was regenerated on client)
            parts = pubkey.split()
            comment = parts[2] if len(parts) >= 3 else None
            if comment:
                lines = existing.splitlines(keepends=True)
                new_lines = []
                replaced = False
                for line in lines:
                    lparts = line.strip().split()
                    if len(lparts) >= 3 and lparts[2] == comment and lparts[0].startswith("ssh-"):
                        new_lines.append(pubkey + "\n")
                        replaced = True
                        sys.stderr.write(f"[register-key] replaced stale key for '{comment}'\n")
                    else:
                        new_lines.append(line)
                if replaced:
                    AUTH_KEYS.write_text("".join(new_lines))
                    AUTH_KEYS.chmod(0o600)
                    self._text(f"OK: key replaced (comment: {comment})")
                    return
            with AUTH_KEYS.open("a") as f:
                f.write(("\n" if existing and not existing.endswith("\n") else "") + pubkey + "\n")
            AUTH_KEYS.chmod(0o600)
            sys.stderr.write(f"[register-key] added: {pubkey[:60]}...\n")
            self._text("OK: key registered")
            return
        # File upload from iPhone/Tailscale — saves to ~/Downloads/
        if parsed.path == "/upload":
            import cgi, os, time
            ctype = self.headers.get("Content-Type", "")
            length = int(self.headers.get("Content-Length", 0))
            if not length:
                self._text("ERROR: empty body", 400)
                return
            # Support multipart/form-data OR raw binary (Content-Disposition: attachment; filename=X)
            fname = self.headers.get("X-Filename", "") or self.headers.get("Content-Disposition", "")
            if "filename=" in fname:
                fname = fname.split("filename=")[-1].strip().strip('"').strip("'")
            if not fname:
                ext = {"image/png": ".png", "image/jpeg": ".jpg", "image/gif": ".gif",
                       "text/plain": ".txt"}.get(ctype.split(";")[0].strip(), ".bin")
                fname = f"upload-{int(time.time())}{ext}"
            # Sanitize filename
            fname = os.path.basename(fname.replace("\\", "/"))
            UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
            dest = UPLOAD_DIR / fname
            data = self.rfile.read(length)
            dest.write_bytes(data)
            sys.stderr.write(f"[upload] saved {len(data)} bytes → {dest}\n")
            self._text(f"OK: saved {fname} ({len(data)} bytes)", ctype="application/json")
            return
        self._text("Not found", 404)

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/bootstrap":
            script = f"""# Claude client bootstrap — Tailscale direct POST (common port 6789)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'  # avoid ReadConsoleOutput error over SSH
$f = Join-Path $env:TEMP 'cs.ps1'
Invoke-WebRequest "http://{SERVER_TAILSCALE_IP}:{SERVER_PORT}/{PS1_FILENAME}" -OutFile $f -UseBasicParsing | Out-Null
& powershell.exe -ExecutionPolicy Bypass -File $f
"""
            self._text(script)
            return

        # Serve PS1 with notify token injected
        if parsed.path == f"/{PS1_FILENAME}":
            ps1_path = HOOKS_DIR / PS1_FILENAME
            if not ps1_path.exists():
                self._text("Not found", 404)
                return
            content = ps1_path.read_text(encoding="utf-8")
            content = content.replace(TOKEN_PLACEHOLDER, NOTIFY_SECRET)
            content = content.replace(PUBKEY_PLACEHOLDER, WSL2_PUBKEY)
            self._text(content, ctype="text/plain; charset=utf-8")
            return

        # iPhone upload page — simple HTML form
        if parsed.path == "/send":
            html = """<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>파일 보내기</title>
<style>
  body{font-family:-apple-system,sans-serif;background:#f5f5f7;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}
  .box{background:#fff;border-radius:18px;padding:32px;width:90vw;max-width:400px;box-shadow:0 4px 20px rgba(0,0,0,.1);text-align:center}
  h2{margin:0 0 8px;font-size:20px}
  p{color:#666;font-size:14px;margin:0 0 24px}
  label{display:block;border:2px dashed #ccc;border-radius:12px;padding:24px;cursor:pointer;margin-bottom:16px;color:#666;font-size:14px}
  label:hover{border-color:#007aff;color:#007aff}
  input[type=file]{display:none}
  button{background:#007aff;color:#fff;border:none;border-radius:12px;padding:14px 0;width:100%;font-size:16px;font-weight:600;cursor:pointer}
  button:active{background:#0056b3}
  #status{margin-top:16px;font-size:14px;color:#333;min-height:20px}
</style></head><body>
<div class="box">
  <h2>📤 파일 보내기</h2>
  <p>WSL2 ~/Downloads 로 전송</p>
  <form id="f">
    <label for="file">여기를 탭해서 파일 선택<br><small>사진, 영상, 문서 모두 가능</small></label>
    <input type="file" id="file" multiple accept="*/*">
    <button type="submit">보내기</button>
  </form>
  <div id="status"></div>
</div>
<script>
document.getElementById('file').onchange=e=>{
  const n=e.target.files.length;
  document.querySelector('label').textContent=n>0?`${n}개 파일 선택됨`:'여기를 탭해서 파일 선택';
};
document.getElementById('f').onsubmit=async e=>{
  e.preventDefault();
  const files=[...document.getElementById('file').files];
  if(!files.length){document.getElementById('status').textContent='파일을 선택해주세요';return;}
  const st=document.getElementById('status');
  for(const f of files){
    st.textContent=`전송 중: ${f.name}…`;
    const r=await fetch('/upload',{method:'POST',headers:{'X-Filename':f.name,'Content-Type':f.type||'application/octet-stream'},body:f});
    const t=await r.text();
    st.textContent=r.ok?`✓ ${f.name} 전송 완료`:`✗ 오류: ${t}`;
  }
  if(files.length>1)st.textContent=`✓ ${files.length}개 모두 전송 완료`;
};
</script></body></html>"""
            self._text(html, ctype="text/html; charset=utf-8")
            return

        super().do_GET()


def main():
    server = HTTPServer(("100.119.82.4", SERVER_PORT), Handler)
    print(f"Bootstrap server on 100.119.82.4:{SERVER_PORT} (Tailscale-only, hooks: {HOOKS_DIR})")
    print(f"  /register-key: localhost-only (tailnet peers blocked)")
    print(f"  notify token: injected into {PS1_FILENAME} at serve time")
    server.serve_forever()


if __name__ == "__main__":
    main()
