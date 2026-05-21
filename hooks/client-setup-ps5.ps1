# client-setup-ps5.ps1 — SSH-only installer (6789 listener removed).
# Original backed up at: client-setup-ps5.ps1.bak.20260520
#
# What it does (idempotent + reversible):
#   6. Writes SSH config entry for home-wsl in ~/.ssh/config
#   7. Generates ed25519 key (if missing) and registers with WSL2
#   8. Enables/installs Windows OpenSSH Server (sshd, port 22)
#   9. Adds WSL2 public key to administrators_authorized_keys
#
# Uninstall SSH only:
#   Stop-Service sshd; Set-Service sshd -StartupType Disabled
#   Remove-NetFirewallRule -Name 'OpenSSH-Server-In-TCP'

$ErrorActionPreference = 'Stop'
$HomeDir      = $env:USERPROFILE
$NotifyToken  = "NOTIFY_TOKEN_HERE"

Write-Host "=== Claude SSH Setup (PS5 native — listener-free) ===" -ForegroundColor Cyan
Write-Host "User: $env:USERNAME   Host: $env:COMPUTERNAME"

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
"@

$existingConfig = if (Test-Path $SshConfig) {
    [System.IO.File]::ReadAllText($SshConfig)
} else { "" }
$existingConfig = ($existingConfig -replace "(?ms)^Host home-wsl\b.*?(?=^Host \S|\z)", "").TrimEnd()
[System.IO.File]::WriteAllText($SshConfig, ($existingConfig + $wslEntry), [System.Text.Encoding]::ASCII)
Write-Host "  [6/9] SSH config: home-wsl written (key: $KeyName)" -ForegroundColor Green

# ------------------------------------------------------------
# 7. Generate SSH key (if missing) + register with WSL2
# ------------------------------------------------------------
if (-not (Test-Path $KeyFile)) {
    Write-Host "  [7/9] Generating ed25519 key: $KeyName ..." -ForegroundColor Cyan
    & ssh-keygen -t ed25519 -C $Hostname -f $KeyFile -N '""' 2>&1 | Out-Null
    Write-Host "  [7/9] Key generated: $KeyFile" -ForegroundColor Green
} else {
    Write-Host "  [7/9] Key exists: $KeyFile" -ForegroundColor Gray
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
            Write-Host "  [7/9] WSL2 authorized_keys: $($resp.Content)" -ForegroundColor Green
            $registered = $true
            break
        } catch {
            if ($attempt -eq 1) {
                Write-Host "  [7/9] Register attempt 1 failed, retrying in 3s..." -ForegroundColor Yellow
                Start-Sleep 3
            } else {
                Write-Host "  [7/9] WARN: could not auto-register key after 2 attempts." -ForegroundColor Red
                Write-Host "        Run manually on WSL2:" -ForegroundColor Yellow
                Write-Host "        echo '$pubkey' >> ~/.ssh/authorized_keys" -ForegroundColor Yellow
            }
        }
    }

    Write-Host "  [7/9] Verifying SSH connectivity to WSL2..." -ForegroundColor Cyan
    $sshTest = & ssh -o BatchMode=yes -o ConnectTimeout=8 -o StrictHostKeyChecking=no `
        -i $KeyFile "desk-1@100.119.82.4" "echo SSH_OK" 2>&1
    if ($sshTest -match "SSH_OK") {
        Write-Host "  [7/9] SSH verification PASSED — home-wsl is ready" -ForegroundColor Green
    } else {
        Write-Host "  [7/9] SSH verification FAILED — key not accepted by WSL2" -ForegroundColor Red
        Write-Host "        echo '$pubkey' >> ~/.ssh/authorized_keys" -ForegroundColor Yellow
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
        Write-Host "  [8/9] OpenSSH Server: was installed, now started" -ForegroundColor Yellow
    } else {
        Write-Host "  [8/9] OpenSSH Server: already running" -ForegroundColor Gray
    }
} else {
    Write-Host "  [8/9] Installing OpenSSH Server ..." -ForegroundColor Cyan
    $cap = Get-WindowsCapability -Online -Name OpenSSH.Server* | Select-Object -First 1
    if ($cap -and $cap.State -ne 'Installed') {
        Add-WindowsCapability -Online -Name $cap.Name | Out-Null
    }
    Start-Service sshd
    Set-Service -Name sshd -StartupType Automatic
    Write-Host "  [8/9] OpenSSH Server: installed and started" -ForegroundColor Green
}

$fwSsh = Get-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -ErrorAction SilentlyContinue
if (-not $fwSsh) {
    New-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -DisplayName 'OpenSSH Server (sshd)' `
        -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22 | Out-Null
    Write-Host "  [8/9] Firewall: port 22 opened" -ForegroundColor Green
} else {
    Write-Host "  [8/9] Firewall: port 22 rule already exists" -ForegroundColor Gray
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
    icacls $AdminKeyFile /inheritance:r /grant "SYSTEM:(F)" /grant "Administrators:(F)" 2>$null | Out-Null
    Write-Host "  [9/9] WSL2 pubkey added to administrators_authorized_keys" -ForegroundColor Green
} else {
    Write-Host "  [9/9] WSL2 pubkey already in administrators_authorized_keys" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=== DONE ===" -ForegroundColor Green
Write-Host "SSH-only setup complete. Port 6789 listener NOT installed."
Write-Host "To install the notification listener separately, run: irm http://100.119.82.4:9955/bootstrap-listener | iex"
