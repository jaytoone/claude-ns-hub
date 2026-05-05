# client-setup-ps5.ps1 — PowerShell-5-native installer for Claude remote-notify listener.
# Architecture: Tailscale direct POST (no SSH tunnel). All clients share port 6789.
# WSL2 hooks enumerate tailnet devices and POST to each client's Tailscale IP:6789.
#
# What it does (idempotent + reversible):
#   1. Writes %USERPROFILE%\claude-notify-listener.ps1 (binds 0.0.0.0:6789)
#   2. Registers URL ACL and Windows Firewall inbound rule for port 6789
#   3. Registers Task Scheduler 'ClaudeNotifyListener' + starts it (survives SSH disconnect)
#   4. Self-tests: POSTs to localhost:6789/notify — square popup should appear
#
# Uninstall:
#   Unregister-ScheduledTask -TaskName ClaudeNotifyListener -Confirm:$false
#   Stop-Process -Name powershell -ErrorAction SilentlyContinue
#   Remove-NetFirewallRule -DisplayName 'Claude Notify 6789'
#   netsh http delete urlacl url=http://+:6789/

$ErrorActionPreference = 'Stop'
$HomeDir      = $env:USERPROFILE
$ListenerPath = Join-Path $HomeDir 'claude-notify-listener.ps1'
$TaskName     = 'ClaudeNotifyListener'
$ListenPort   = 6789
$NotifyToken  = "NOTIFY_TOKEN_HERE"

Write-Host "=== Claude Notify — Client Setup (PS5 native) ===" -ForegroundColor Cyan
Write-Host "User: $env:USERNAME   Host: $env:COMPUTERNAME"
Write-Host "Architecture: Tailscale direct POST on 0.0.0.0:$ListenPort (no SSH tunnel)"

# ------------------------------------------------------------
# 1. Write the listener PS1 (embedded inline)
# ------------------------------------------------------------
$listenerBody = @'
# claude-notify-listener.ps1 — Session 0 version. Popups spawn without console flash.
# Clipboard requests written to %LOCALAPPDATA%\claude-clip-bridge\pending.txt for Session 1 daemon.

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Shared secret injected at bootstrap time — validates /clipboard, /expose, /unexpose requests
$NotifyToken = "NOTIFY_TOKEN_HERE"

$port = 6789
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://+:$port/")
try { $listener.Start() } catch {
    Add-Content "$env:USERPROFILE\claude-notify-listener.err" "start fail: $_"
    exit 1
}

$SlotDir = Join-Path $env:LOCALAPPDATA "claude-notify-slots"
if (-not (Test-Path $SlotDir)) { New-Item -ItemType Directory -Force -Path $SlotDir | Out-Null }
$ClipBridge = Join-Path $env:LOCALAPPDATA "claude-clip-bridge"
if (-not (Test-Path $ClipBridge)) { New-Item -ItemType Directory -Force -Path $ClipBridge | Out-Null }

$SqSz = 60
$Gap = 6

function Cleanup-StaleSlots {
    Get-ChildItem $SlotDir -Filter "slot_*.pid" -ErrorAction SilentlyContinue | ForEach-Object {
        try {
            $p = Get-Content $_.FullName -ErrorAction Stop
            if (-not $p -or -not (Get-Process -Id $p -ErrorAction SilentlyContinue)) {
                $base = $_.BaseName
                Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
                Remove-Item (Join-Path $SlotDir "$base.proj") -Force -ErrorAction SilentlyContinue
                Remove-Item (Join-Path $SlotDir "$base.close") -Force -ErrorAction SilentlyContinue
            }
        } catch {}
    }
}

function Get-FreeSlot {
    Cleanup-StaleSlots
    for ($i = 0; $i -lt 10; $i++) {
        if (-not (Test-Path (Join-Path $SlotDir "slot_$i.pid"))) { return $i }
    }
    return 0
}

function Close-ProjectPopups($projKey) {
    Get-ChildItem $SlotDir -Filter "slot_*.proj" -ErrorAction SilentlyContinue | ForEach-Object {
        try {
            if ((Get-Content $_.FullName -ErrorAction Stop) -eq $projKey) {
                New-Item -ItemType File -Force -Path (Join-Path $SlotDir ($_.BaseName + ".close")) | Out-Null
            }
        } catch {}
    }
}

function Parse-Label($title) {
    if ($title -match '^\[(\d+)\]') { return $matches[1] }
    $t = ($title -replace '[^A-Za-z0-9]','').Trim()
    if ($t) { return $t.Substring(0, [Math]::Min(2, $t.Length)) }
    return '!'
}

function Parse-ProjKey($title) {
    if ($title -match '^\[\d+\]\s+(.+)$') { return $matches[1].Trim() }
    return $title.Trim()
}

function Show-Square($title, $kind, $slot, $label, $projKey) {
    $slotFile  = Join-Path $SlotDir "slot_$slot.pid"
    $projFile  = Join-Path $SlotDir "slot_$slot.proj"
    $closeFile = Join-Path $SlotDir "slot_$slot.close"
    Set-Content -Path $projFile -Value $projKey -Encoding ASCII
    Remove-Item $closeFile -Force -ErrorAction SilentlyContinue
    $slotFileWin  = $slotFile.Replace('\','\\')
    $closeFileWin = $closeFile.Replace('\','\\')
    $projFileWin  = $projFile.Replace('\','\\')
    $cls = "WinN" + (Get-Random -Maximum 999999)
    $offset = $slot * ($SqSz + $Gap)
    $lbl = ($label -replace "'","''")
    $ttl = ($title -replace "'","''")
    $color = if ($kind -eq 'stop') { '100,220,120' } else { '135,206,250' }

    $psCode = @"
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
`$_cs = 'using System; using System.Runtime.InteropServices; public class CLSNAME { [DllImport("Gdi32.dll")] public static extern IntPtr CreateRoundRectRgn(int x1,int y1,int x2,int y2,int cx,int cy); [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hInsertAfter, int x, int y, int cx, int cy, uint flags); [DllImport("dwmapi.dll")] public static extern int DwmSetWindowAttribute(IntPtr hwnd, int attr, ref int attrValue, int attrSize); }' -replace 'CLSNAME','$cls'
Add-Type -TypeDefinition `$_cs
[System.IO.File]::WriteAllText('$slotFileWin', [string][System.Diagnostics.Process]::GetCurrentProcess().Id)
`$form = New-Object System.Windows.Forms.Form
`$form.FormBorderStyle = 'None'
`$form.BackColor = [System.Drawing.Color]::FromArgb(22,22,35)
`$form.Width = $SqSz; `$form.Height = $SqSz
`$form.Opacity = 0.95
`$form.TopMost = `$true
`$form.ShowInTaskbar = `$false
`$form.StartPosition = 'Manual'
`$form.Cursor = [System.Windows.Forms.Cursors]::Hand
`$form.Text = '$ttl'
`$sw = [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea
`$form.Left = [int](`$sw.Width / 8) + $offset
`$form.Top  = `$sw.Bottom - $SqSz - [int](`$sw.Height / 16)
`$form.Add_Shown({
    `$rgn = [$cls]::CreateRoundRectRgn(-2,-2,$($SqSz+2),$($SqSz+2),14,14)
    `$form.Region = [System.Drawing.Region]::FromHrgn(`$rgn)
    [$cls]::SetWindowPos(`$form.Handle, [IntPtr](-1), 0, 0, 0, 0, 0x0013)
    `$dwmNoBorder = -2; `$dwmNoRound = 1
    try { [$cls]::DwmSetWindowAttribute(`$form.Handle, 34, [ref]`$dwmNoBorder, 4) } catch {}
    try { [$cls]::DwmSetWindowAttribute(`$form.Handle, 33, [ref]`$dwmNoRound, 4) } catch {}
})
`$form.Add_Click({ `$form.Close() })
`$script:hovering = `$false
`$form.Add_MouseEnter({ `$script:hovering = `$true; `$form.Opacity = 0.95 })
`$form.Add_MouseLeave({ `$script:hovering = `$false; `$elapsed2 = ([DateTime]::Now - `$startTime).TotalSeconds; `$form.Opacity = if (`$elapsed2 -ge 1800) { 0.40 } else { [Math]::Max(0.40, 0.95 - (0.55 * [Math]::Sqrt(`$elapsed2 / 1800))) } })
`$lblCtl = New-Object System.Windows.Forms.Label
`$lblCtl.Text = '$lbl'
`$lblCtl.ForeColor = [System.Drawing.Color]::FromArgb($color)
`$lblCtl.BackColor = [System.Drawing.Color]::Transparent
`$lblCtl.Font = New-Object System.Drawing.Font('Segoe UI',22,[System.Drawing.FontStyle]::Bold)
`$lblCtl.TextAlign = [System.Drawing.ContentAlignment]::MiddleCenter
`$lblCtl.Location = '0,0'; `$lblCtl.Size = '$SqSz,$SqSz'
`$lblCtl.Cursor = [System.Windows.Forms.Cursors]::Hand
`$lblCtl.Add_Click({ `$form.Close() })
`$lblCtl.Add_MouseEnter({ `$script:hovering = `$true; `$form.Opacity = 0.95 })
`$lblCtl.Add_MouseLeave({ `$script:hovering = `$false; `$elapsed2 = ([DateTime]::Now - `$startTime).TotalSeconds; `$form.Opacity = if (`$elapsed2 -ge 1800) { 0.40 } else { [Math]::Max(0.40, 0.95 - (0.55 * [Math]::Sqrt(`$elapsed2 / 1800))) } })
`$form.Controls.Add(`$lblCtl)
try { [System.Media.SystemSounds]::Exclamation.Play() } catch {}
`$topTimer = New-Object System.Windows.Forms.Timer
`$topTimer.Interval = 500
`$topTimer.Add_Tick({
    [$cls]::SetWindowPos(`$form.Handle, [IntPtr](-1), 0, 0, 0, 0, 0x0013)
    if ([System.IO.File]::Exists('$closeFileWin')) { `$form.Close() }
})
`$topTimer.Start()
`$startTime = [DateTime]::Now
`$fadeTimer = New-Object System.Windows.Forms.Timer
`$fadeTimer.Interval = 1000
`$fadeTimer.Add_Tick({
    if (`$script:hovering) { return }
    `$elapsed = ([DateTime]::Now - `$startTime).TotalSeconds
    if (`$elapsed -ge 1800) { `$form.Opacity = 0.40; `$fadeTimer.Stop() }
    else { `$form.Opacity = 0.95 - (0.55 * [Math]::Sqrt(`$elapsed / 1800)) }
})
`$fadeTimer.Start()
`$form.Add_FormClosed({
    Remove-Item '$slotFileWin' -Force -ErrorAction SilentlyContinue
    Remove-Item '$projFileWin' -Force -ErrorAction SilentlyContinue
    Remove-Item '$closeFileWin' -Force -ErrorAction SilentlyContinue
})
[System.Windows.Forms.Application]::Run(`$form)
"@
    $encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($psCode))
    Start-Process powershell.exe -ArgumentList "-NoProfile","-STA","-WindowStyle","Hidden","-EncodedCommand",$encoded -WindowStyle Hidden | Out-Null
}

function Set-RemoteClipboard($text) {
    if ([string]::IsNullOrEmpty($text)) { return }
    try { Set-Clipboard -Value $text } catch {
        $tmp = [IO.Path]::GetTempFileName()
        [IO.File]::WriteAllText($tmp, $text, [Text.Encoding]::Unicode)
        cmd /c "clip < `"$tmp`""
        Remove-Item $tmp -Force -ErrorAction SilentlyContinue
    }
}

while ($listener.IsListening) {
    try {
        $ctx = $listener.GetContext()
        $req = $ctx.Request
        $res = $ctx.Response

        if ($req.HttpMethod -eq 'GET' -and ($req.Url.AbsolutePath -eq '/' -or $req.Url.AbsolutePath -eq '/health')) {
            $bytes = [Text.Encoding]::UTF8.GetBytes('ok')
            $res.OutputStream.Write($bytes, 0, $bytes.Length)
            $res.Close()
            continue
        }

        if ($req.HttpMethod -eq 'POST' -and $req.Url.AbsolutePath -eq '/notify') {
            if ($req.Headers["X-Notify-Token"] -ne $NotifyToken) {
                $res.StatusCode = 403
                $bytes = [Text.Encoding]::UTF8.GetBytes('Forbidden')
                $res.OutputStream.Write($bytes, 0, $bytes.Length); $res.Close(); continue
            }
            $reader = New-Object IO.StreamReader($req.InputStream, [Text.Encoding]::UTF8)
            $body = $reader.ReadToEnd()
            $reader.Dispose()
            $title = 'Claude'; $kind = 'notify'
            try {
                $obj = $body | ConvertFrom-Json -ErrorAction Stop
                if ($obj.title) { $title = [string]$obj.title }
                if ($obj.kind) { $kind = [string]$obj.kind }
            } catch {}
            $projKey = Parse-ProjKey $title
            Close-ProjectPopups $projKey
            Start-Sleep -Milliseconds 400
            $slot = Get-FreeSlot
            $label = Parse-Label $title
            Show-Square $title $kind $slot $label $projKey
            $bytes = [Text.Encoding]::UTF8.GetBytes('ok')
            $res.OutputStream.Write($bytes, 0, $bytes.Length)
            $res.Close()
            continue
        }

        if ($req.HttpMethod -eq 'POST' -and $req.Url.AbsolutePath -eq '/clipboard') {
            if ($req.Headers["X-Notify-Token"] -ne $NotifyToken) {
                $res.StatusCode = 403
                $bytes = [Text.Encoding]::UTF8.GetBytes('Forbidden')
                $res.OutputStream.Write($bytes, 0, $bytes.Length); $res.Close(); continue
            }
            $reader = New-Object IO.StreamReader($req.InputStream, [Text.Encoding]::UTF8)
            $body = $reader.ReadToEnd()
            $reader.Dispose()
            Set-RemoteClipboard $body
            $bytes = [Text.Encoding]::UTF8.GetBytes('ok')
            $res.OutputStream.Write($bytes, 0, $bytes.Length)
            $res.Close()
            continue
        }

        if ($req.HttpMethod -eq 'POST' -and $req.Url.AbsolutePath -eq '/close') {
            if ($req.Headers["X-Notify-Token"] -ne $NotifyToken) {
                $res.StatusCode = 403
                $bytes = [Text.Encoding]::UTF8.GetBytes('Forbidden')
                $res.OutputStream.Write($bytes, 0, $bytes.Length); $res.Close(); continue
            }
            $reader = New-Object IO.StreamReader($req.InputStream, [Text.Encoding]::UTF8)
            $body = $reader.ReadToEnd()
            $reader.Dispose()
            $projKey = $null
            try {
                $obj = $body | ConvertFrom-Json -ErrorAction Stop
                if ($obj.proj_key) { $projKey = [string]$obj.proj_key }
            } catch { $projKey = $body.Trim() }
            if ($projKey) { Close-ProjectPopups $projKey }
            $bytes = [Text.Encoding]::UTF8.GetBytes('ok')
            $res.OutputStream.Write($bytes, 0, $bytes.Length)
            $res.Close()
            continue
        }

        # /expose — dynamic same-URL mirror: client localhost:<port> → WSL2 localhost:<port>
        if ($req.HttpMethod -eq 'POST' -and $req.Url.AbsolutePath -eq '/expose') {
            if ($req.Headers["X-Notify-Token"] -ne $NotifyToken) {
                $res.StatusCode = 403
                $bytes = [Text.Encoding]::UTF8.GetBytes('Forbidden')
                $res.OutputStream.Write($bytes, 0, $bytes.Length); $res.Close(); continue
            }
            $reader = New-Object IO.StreamReader($req.InputStream, [Text.Encoding]::UTF8)
            $body = $reader.ReadToEnd()
            $reader.Dispose()
            $port = 0
            try { $port = [int](($body | ConvertFrom-Json).port) } catch {}
            if ($port -gt 0 -and $port -le 65535) {
                & netsh interface portproxy delete v4tov4 listenaddress=127.0.0.1 listenport=$port 2>$null | Out-Null
                & netsh interface portproxy add v4tov4 listenaddress=127.0.0.1 listenport=$port connectaddress=100.119.82.4 connectport=$port 2>$null | Out-Null
                $bytes = [Text.Encoding]::UTF8.GetBytes("exposed $port")
            } else {
                $res.StatusCode = 400
                $bytes = [Text.Encoding]::UTF8.GetBytes('invalid port')
            }
            $res.OutputStream.Write($bytes, 0, $bytes.Length)
            $res.Close()
            continue
        }

        # /unexpose — remove mirror for given port
        if ($req.HttpMethod -eq 'POST' -and $req.Url.AbsolutePath -eq '/unexpose') {
            if ($req.Headers["X-Notify-Token"] -ne $NotifyToken) {
                $res.StatusCode = 403
                $bytes = [Text.Encoding]::UTF8.GetBytes('Forbidden')
                $res.OutputStream.Write($bytes, 0, $bytes.Length); $res.Close(); continue
            }
            $reader = New-Object IO.StreamReader($req.InputStream, [Text.Encoding]::UTF8)
            $body = $reader.ReadToEnd()
            $reader.Dispose()
            $port = 0
            try { $port = [int](($body | ConvertFrom-Json).port) } catch {}
            if ($port -gt 0 -and $port -le 65535) {
                & netsh interface portproxy delete v4tov4 listenaddress=127.0.0.1 listenport=$port 2>$null | Out-Null
                $bytes = [Text.Encoding]::UTF8.GetBytes("unexposed $port")
            } else {
                $res.StatusCode = 400
                $bytes = [Text.Encoding]::UTF8.GetBytes('invalid port')
            }
            $res.OutputStream.Write($bytes, 0, $bytes.Length)
            $res.Close()
            continue
        }

        # /exposed — list current portproxy mirrors
        if ($req.HttpMethod -eq 'GET' -and $req.Url.AbsolutePath -eq '/exposed') {
            $out = (& netsh interface portproxy show v4tov4 2>$null | Out-String)
            $bytes = [Text.Encoding]::UTF8.GetBytes($out)
            $res.OutputStream.Write($bytes, 0, $bytes.Length)
            $res.Close()
            continue
        }

        $res.StatusCode = 404
        $res.Close()
    } catch {
        Add-Content "$env:USERPROFILE\claude-notify-listener.err" ("{0}: {1}" -f (Get-Date), $_)
    }
}
'@

Set-Content -Path $ListenerPath -Value $listenerBody -Encoding UTF8
Write-Host "  [1/5] Listener written: $ListenerPath"

# ------------------------------------------------------------
# 2. Register Task Scheduler at logon
# ------------------------------------------------------------
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue | Out-Null

$action    = New-ScheduledTaskAction -Execute 'powershell.exe' `
                 -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$ListenerPath`""
# LogonType MUST be Interactive — S4U runs in Session 0 with NO desktop access,
# which means WinForms popups physically cannot render. We trade session-lifetime
# persistence for UI capability; the 1-min repeat trigger compensates by reviving
# the task within 60s if it dies mid-session.
$localUser     = "$env:COMPUTERNAME\$env:USERNAME"
$triggerLogon  = New-ScheduledTaskTrigger -AtLogOn -User $localUser
$triggerRepeat = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) `
                      -RepetitionInterval (New-TimeSpan -Minutes 1)
$trigger = @($triggerLogon, $triggerRepeat)
$principal = New-ScheduledTaskPrincipal -UserId $localUser -LogonType Interactive -RunLevel Highest
$settings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
                 -StartWhenAvailable -ExecutionTimeLimit ([TimeSpan]::Zero) `
                 -RestartCount 99 -RestartInterval (New-TimeSpan -Minutes 1) `
                 -MultipleInstances IgnoreNew

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger `
                       -Principal $principal -Settings $settings | Out-Null
Write-Host "  [2/5] Task '$TaskName' registered (triggers at logon, auto-restarts on crash)"

# ------------------------------------------------------------
# 3. URL ACL + Windows Firewall rule — MUST run before listener start
# ------------------------------------------------------------
# HttpListener needs wildcard URL ACL to bind non-localhost without admin at runtime
& netsh http delete urlacl url=http://127.0.0.1:$ListenPort/ 2>$null | Out-Null
& netsh http delete urlacl url="http://+:$ListenPort/" 2>$null | Out-Null
& netsh http add urlacl url="http://+:$ListenPort/" user="$env:COMPUTERNAME\$env:USERNAME" 2>$null | Out-Null
Write-Host "  [3a/5] URL ACL registered: http://+:$ListenPort/ for $env:COMPUTERNAME\$env:USERNAME"

# Firewall inbound rule
$fwName = "Claude Notify $ListenPort"
Get-NetFirewallRule -DisplayName $fwName -ErrorAction SilentlyContinue | Remove-NetFirewallRule -ErrorAction SilentlyContinue
New-NetFirewallRule -DisplayName $fwName -Direction Inbound -Protocol TCP `
                     -LocalPort $ListenPort -Action Allow -Profile Any `
                     -ErrorAction SilentlyContinue | Out-Null
Write-Host "  [3b/5] Firewall inbound rule '$fwName' added"

# ------------------------------------------------------------
# 4. Start listener via Task Scheduler (ACL+firewall now in place)
# ------------------------------------------------------------
# Kill by command-line match first (targeted)
Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -like "*claude-notify-listener*" } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }

# Fallback: kill anything holding port 6789 (catches old listeners from prior versions)
try {
    $holders = Get-NetTCPConnection -LocalPort $ListenPort -State Listen -ErrorAction SilentlyContinue |
               Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($pid in $holders) {
        if ($pid -and $pid -ne $PID) {
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        }
    }
} catch {}

# Clear any stale error log from previous failed starts
Remove-Item "$env:USERPROFILE\claude-notify-listener.err" -Force -ErrorAction SilentlyContinue
Start-Sleep 2

Start-ScheduledTask -TaskName $TaskName
Start-Sleep 2
Write-Host "  [4/5] Listener started via Task Scheduler (survives SSH disconnect)"

# ------------------------------------------------------------
# 5. Self-test: POST a local notification
# ------------------------------------------------------------
Start-Sleep 1
try {
    $body = '{"title":"Claude Notify","message":"Setup complete on ' + $env:COMPUTERNAME + '"}'
    Invoke-RestMethod -Uri "http://127.0.0.1:$ListenPort/notify" -Method Post -Body $body -ContentType 'application/json' -Headers @{"X-Notify-Token" = $NotifyToken} | Out-Null
    Write-Host "  [5/5] Self-test POST succeeded — you should see a square popup" -ForegroundColor Green
} catch {
    Write-Host "  [5/5] Self-test POST FAILED: $_" -ForegroundColor Red
    Write-Host "        Check C:\Users\$env:USERNAME\claude-notify-listener.err for listener errors"
}

# ------------------------------------------------------------
# 6. Write SSH config entry for home-wsl
# ------------------------------------------------------------
$SshDir    = Join-Path $env:USERPROFILE ".ssh"
$SshConfig = Join-Path $SshDir "config"
if (-not (Test-Path $SshDir)) { New-Item -ItemType Directory -Force -Path $SshDir | Out-Null }

$Hostname   = $env:COMPUTERNAME.ToLower()
$KeyName    = "id_home_wsl_$Hostname"
$KeyFile    = Join-Path $SshDir $KeyName
$PubKeyFile = "$KeyFile.pub"

$wslEntry = @"

Host home-wsl
    HostName 100.119.82.4
    Port 22
    User desk-1
    IdentityFile ~/.ssh/$KeyName
    ServerAliveInterval 30
    ServerAliveCountMax 3
    RemoteForward 6789 127.0.0.1:6789
"@

$existingConfig = if (Test-Path $SshConfig) { Get-Content $SshConfig -Raw } else { "" }
if ($existingConfig -match "Host home-wsl") {
    $existingConfig = $existingConfig -replace "(?s)(Host home-wsl\s+)HostName\s+[\d.]+", '${1}HostName 100.119.82.4'
    $existingConfig = $existingConfig -replace "(?s)(Host home-wsl(?:.|\n)*?User\s+)\w+", '${1}desk-1'
    $existingConfig = $existingConfig -replace "(?s)(Host home-wsl(?:.|\n)*?IdentityFile\s+~/.ssh/)\S+", "`${1}$KeyName"
    $existingConfig | Set-Content $SshConfig -NoNewline
    Write-Host "  [6/7] SSH config: home-wsl updated (key: $KeyName)" -ForegroundColor Yellow
} else {
    Add-Content $SshConfig $wslEntry
    Write-Host "  [6/7] SSH config: added home-wsl → 100.119.82.4 (key: $KeyName)" -ForegroundColor Green
}

# ------------------------------------------------------------
# 7. Generate SSH key (if missing) + register with WSL2
# ------------------------------------------------------------
if (-not (Test-Path $KeyFile)) {
    Write-Host "  [7/7] Generating ed25519 key: $KeyName ..." -ForegroundColor Cyan
    & ssh-keygen -t ed25519 -C $Hostname -f $KeyFile -N '""' 2>&1 | Out-Null
    Write-Host "  [7/7] Key generated: $KeyFile" -ForegroundColor Green
} else {
    Write-Host "  [7/7] Key exists: $KeyFile" -ForegroundColor Gray
}

if (Test-Path $PubKeyFile) {
    $pubkey = (Get-Content $PubKeyFile -Raw).Trim()
    $registered = $false
    foreach ($attempt in 1..2) {
        try {
            $resp = Invoke-WebRequest `
                -Uri "http://100.119.82.4:9955/register-key" `
                -Method POST `
                -Body $pubkey `
                -ContentType "text/plain" `
                -Headers @{"X-Notify-Token" = $NotifyToken} `
                -UseBasicParsing
            Write-Host "  [7/7] WSL2 authorized_keys: $($resp.Content)" -ForegroundColor Green
            $registered = $true
            break
        } catch {
            if ($attempt -eq 1) {
                Write-Host "  [7/7] Register attempt 1 failed, retrying in 3s..." -ForegroundColor Yellow
                Start-Sleep 3
            } else {
                Write-Host "  [7/7] WARN: could not auto-register key after 2 attempts." -ForegroundColor Red
                Write-Host "        Run manually on WSL2:" -ForegroundColor Yellow
                Write-Host "        echo '$pubkey' >> ~/.ssh/authorized_keys" -ForegroundColor Yellow
            }
        }
    }

    # Verify the key actually works via SSH regardless of registration method
    Write-Host "  [7/7] Verifying SSH connectivity to WSL2..." -ForegroundColor Cyan
    $sshTest = & ssh -o BatchMode=yes -o ConnectTimeout=8 -o StrictHostKeyChecking=no `
        -i $KeyFile "desk-1@100.119.82.4" "echo SSH_OK" 2>&1
    if ($sshTest -match "SSH_OK") {
        Write-Host "  [7/7] SSH verification PASSED — home-wsl is ready" -ForegroundColor Green
    } else {
        Write-Host "  [7/7] SSH verification FAILED — key not accepted by WSL2" -ForegroundColor Red
        Write-Host "        Add this key manually on WSL2 then retry:" -ForegroundColor Yellow
        Write-Host "        echo '$pubkey' >> ~/.ssh/authorized_keys" -ForegroundColor Yellow
        Write-Host "        ssh -i $KeyFile desk-1@100.119.82.4   # test yourself" -ForegroundColor Yellow
    }
}

# ------------------------------------------------------------
# 8. Enable OpenSSH Server (so WSL2 can SSH back into this PC)
# ------------------------------------------------------------
$sshdSvc = Get-Service -Name sshd -ErrorAction SilentlyContinue
if ($sshdSvc) {
    if ($sshdSvc.Status -ne 'Running') {
        Start-Service sshd
        Set-Service -Name sshd -StartupType Automatic
        Write-Host "  [8/8] OpenSSH Server: was installed, now started" -ForegroundColor Yellow
    } else {
        Write-Host "  [8/8] OpenSSH Server: already running" -ForegroundColor Gray
    }
} else {
    Write-Host "  [8/8] Installing OpenSSH Server ..." -ForegroundColor Cyan
    $cap = Get-WindowsCapability -Online -Name OpenSSH.Server* | Select-Object -First 1
    if ($cap -and $cap.State -ne 'Installed') {
        Add-WindowsCapability -Online -Name $cap.Name | Out-Null
    }
    Start-Service sshd
    Set-Service -Name sshd -StartupType Automatic
    Write-Host "  [8/8] OpenSSH Server: installed and started" -ForegroundColor Green
}

# Firewall rule for port 22 (idempotent)
$fwSsh = Get-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -ErrorAction SilentlyContinue
if (-not $fwSsh) {
    New-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -DisplayName 'OpenSSH Server (sshd)' `
        -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22 | Out-Null
    Write-Host "  [8/8] Firewall: port 22 opened" -ForegroundColor Green
} else {
    Write-Host "  [8/8] Firewall: port 22 rule already exists" -ForegroundColor Gray
}

# ------------------------------------------------------------
# 9. Register WSL2's public key → this PC's administrators_authorized_keys
#    (enables WSL2 to SSH back into this Windows machine)
# ------------------------------------------------------------
$Wsl2PubKey  = "WSL2_PUBKEY_HERE"
$AdminKeyFile = "C:\ProgramData\ssh\administrators_authorized_keys"

if (Test-Path $AdminKeyFile) {
    $existing = Get-Content $AdminKeyFile -Raw -ErrorAction SilentlyContinue
} else {
    $existing = ""
    New-Item -ItemType File -Force -Path $AdminKeyFile | Out-Null
}

if ($existing -notmatch [regex]::Escape($Wsl2PubKey.Split(" ")[1])) {
    Add-Content $AdminKeyFile $Wsl2PubKey
    # Permissions: only SYSTEM + Administrators (required by OpenSSH on Windows)
    icacls $AdminKeyFile /inheritance:r /grant "SYSTEM:(F)" /grant "Administrators:(F)" 2>$null | Out-Null
    Write-Host "  [9/9] WSL2 pubkey added to administrators_authorized_keys" -ForegroundColor Green
} else {
    Write-Host "  [9/9] WSL2 pubkey already in administrators_authorized_keys" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=== DONE ===" -ForegroundColor Green
$myTs = (& tailscale ip -4 2>$null | Select-Object -First 1)
if ($myTs) {
    Write-Host "Tailscale IP: $myTs — WSL2 hooks will POST directly to http://${myTs}:$ListenPort/notify"
} else {
    Write-Host "Note: Tailscale CLI not found on PATH. Ensure Tailscale is running and you are signed in."
}
Write-Host "No SSH tunnel needed — notifications work whenever this PC is online on the tailnet."
