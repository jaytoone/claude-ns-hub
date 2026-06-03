@echo off
setlocal EnableDelayedExpansion

echo ================================================================
echo   claude-ns-hub  --  Windows Install Script (M524.4)
echo   Requires: Python 3.11+, pip, Windows 10/11 or Windows Server
echo   Recommended: Run inside WSL2 for full exec-session support
echo ================================================================
echo.

:: ------------------------------------------------------------------
:: 1. Check Python
:: ------------------------------------------------------------------
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Download from https://www.python.org/downloads/
    echo         Ensure "Add Python to PATH" is checked during install.
    pause & exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PY_VER=%%v
echo [OK] Python %PY_VER% found.

:: ------------------------------------------------------------------
:: 2. pip install claude-ns-hub
:: ------------------------------------------------------------------
echo.
echo [1/4] Installing claude-ns-hub via pip...
python -m pip install --upgrade claude-ns-hub
if errorlevel 1 (
    echo [ERROR] pip install failed. Check internet connection and pip version.
    pause & exit /b 1
)
echo [OK] claude-ns-hub installed.

:: ------------------------------------------------------------------
:: 3. Verify 'hub' command resolves
:: ------------------------------------------------------------------
echo.
echo [2/4] Verifying 'hub' command...
where hub >nul 2>&1
if errorlevel 1 (
    echo [WARN] 'hub' not found in PATH. Adding Scripts dir to user PATH...
    for /f "delims=" %%p in ('python -c "import sys; print(sys.exec_prefix)"') do set PY_PREFIX=%%p
    set SCRIPTS_DIR=!PY_PREFIX!\Scripts
    setx PATH "!PATH!;!SCRIPTS_DIR!" /M >nul 2>&1
    if errorlevel 1 (
        setx PATH "!PATH!;!SCRIPTS_DIR!" >nul 2>&1
    )
    echo [OK] Added !SCRIPTS_DIR! to PATH. Restart terminal after install.
) else (
    for /f "delims=" %%h in ('where hub') do echo [OK] hub found at %%h
)

:: ------------------------------------------------------------------
:: 4. Firewall rule (allow inbound TCP 9000)
:: ------------------------------------------------------------------
echo.
echo [3/4] Adding Windows Firewall rule for port 9000...
netsh advfirewall firewall show rule name="claude-ns-hub" >nul 2>&1
if errorlevel 1 (
    netsh advfirewall firewall add rule name="claude-ns-hub" dir=in action=allow protocol=TCP localport=9000 >nul 2>&1
    if errorlevel 1 (
        echo [WARN] Could not add firewall rule (run as Administrator to add).
    ) else (
        echo [OK] Firewall rule added: TCP 9000 inbound allowed.
    )
) else (
    echo [OK] Firewall rule already exists.
)

:: ------------------------------------------------------------------
:: 5. Task Scheduler: auto-start hub at login
:: ------------------------------------------------------------------
echo.
echo [4/4] Registering Task Scheduler task for auto-start at login...
schtasks /query /tn "claude-ns-hub" >nul 2>&1
if not errorlevel 1 (
    echo [OK] Task Scheduler task already registered.
    goto done
)

:: Find hub.exe path
for /f "delims=" %%h in ('where hub 2^>nul') do set HUB_EXE=%%h
if not defined HUB_EXE (
    for /f "delims=" %%p in ('python -c "import sys; print(sys.exec_prefix)"') do set HUB_EXE=%%p\Scripts\hub.exe
)

schtasks /create /tn "claude-ns-hub" /tr "\"!HUB_EXE!\"" /sc ONLOGON /rl LIMITED /f >nul 2>&1
if errorlevel 1 (
    echo [WARN] Could not create Task Scheduler task. To start manually: hub
    echo        To register manually (Admin PowerShell):
    echo          schtasks /create /tn "claude-ns-hub" /tr "\"!HUB_EXE!\"" /sc ONLOGON /rl HIGHEST /f
) else (
    echo [OK] Task Scheduler task registered — hub will start at next login.
)

:done
echo.
echo ================================================================
echo   Install complete.
echo.
echo   Start now:    hub
echo   Open browser: http://localhost:9000
echo.
echo   NOTE: Full exec-session support (Execute button) requires tmux.
echo         Run 'wsl --install' to enable WSL2, then 'hub' inside WSL2.
echo ================================================================
echo.
pause
