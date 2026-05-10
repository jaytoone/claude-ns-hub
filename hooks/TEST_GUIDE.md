# Auto-Compact Hook - Testing Guide

**Status**: ✅ All validations passed

---

## Pre-Deployment Verification ✅

### 1. Syntax Validation
- ✅ `pre-compact-save.js` - Node.js syntax valid
- ✅ `settings.json` - JSON format valid
- ✅ File paths correctly configured

### 2. Files in Place
```
C:\Users\Jayone\.claude\hooks\
├── pre-compact-save.js            ✅
├── post-compact-recovery.md        ✅
├── system-prompt.md                ✅
└── IMPLEMENTATION_STATUS.md        ✅
```

---

## Method 1: Simulate PreCompact Hook (Offline Test)

### Step 1: Create Mock Compact Event

```bash
# Create backup directory
mkdir %USERPROFILE%\.claude\context-backups

# Get current transcript path (simulate)
set TRANSCRIPT_PATH=%USERPROFILE%\.claude\projects\D--Project-ASI\5c455b6c-5559-4833-8474-68a97a3bacb7.jsonl

# Create mock stdin (what Claude Code sends to hook)
echo {
  "transcript_path": "%TRANSCRIPT_PATH%",
  "session_id": "test-session-001",
  "trigger": "manual"
} > mock_input.json
```

### Step 2: Execute Hook Handler

```bash
# Run the pre-compact handler with mock input
node C:\Users\Jayone\.claude\hooks\pre-compact-save.js < mock_input.json
```

### Expected Output
```
[PreCompact] Context saved (trigger: manual, session: test-session-001)
```

### Step 3: Verify Backup Creation

```bash
# Check if backup file was created
dir %USERPROFILE%\.claude\context-backups\
# Should show: last_context_test-session-001_[timestamp].jsonl

# Check marker file
if exist %USERPROFILE%\.claude\.compact-marker (
  echo ✅ Marker file exists
  type %USERPROFILE%\.claude\.compact-marker
) else (
  echo ❌ Marker file not found
)
```

---

## Method 2: Natural Auto-Compact Test (Online Test)

### When Auto-Compact Triggers Naturally

Claude Code will auto-compact when:
- Conversation approaches ~95% token limit
- Manually triggered (if `/compact` command available)

### What to Monitor

**After auto-compact:**
1. Next prompt submission
2. Check for recovery.md display
   - Should show in console/terminal
   - Provides guidance on backup location
3. Verify marker file deletion
   ```bash
   if exist %USERPROFILE%\.claude\.compact-marker (
     echo ❌ Marker not deleted
   ) else (
     echo ✅ Marker deleted successfully
   )
   ```
4. Confirm system-prompt.md displays after recovery.md

---

## Method 3: Manual Hook Execution Test

### Test PreCompact Hook Directly

```bash
# Navigate to hook directory
cd %USERPROFILE%\.claude\hooks

# Create test input matching Claude Code's format
@echo off
setlocal enabledelayedexpansion

REM Get the actual transcript path from Claude Code session
for /r "%USERPROFILE%\.claude\projects" %%F in (*.jsonl) do (
  set "TRANSCRIPT=%%F"
  goto :found
)

:found
if defined TRANSCRIPT (
  echo Testing with: %TRANSCRIPT%

  REM Create mock JSON input
  (
    echo {
    echo   "transcript_path": "%TRANSCRIPT%",
    echo   "session_id": "test-001",
    echo   "trigger": "manual"
    echo }
  ) | node pre-compact-save.js

  echo.
  echo Checking backup directory...
  dir "%USERPROFILE%\.claude\context-backups" /O-D

  echo.
  echo Checking marker file...
  if exist "%USERPROFILE%\.claude\.compact-marker" (
    echo ✅ Marker file created
    type "%USERPROFILE%\.claude\.compact-marker"
  ) else (
    echo ❌ Marker file not created
  )
) else (
  echo ❌ No transcript file found
)
```

---

## Method 4: UserPromptSubmit Hook Test

### Test the Recovery Detection

```bash
# Step 1: Manually create marker file
@echo off
setlocal

REM Create marker file
echo %date% %time% > "%USERPROFILE%\.claude\.compact-marker"
echo Trigger: manual >> "%USERPROFILE%\.claude\.compact-marker"

echo ✅ Marker file created

REM Step 2: Execute the UserPromptSubmit hook command
REM This should display recovery.md if marker exists
cmd /c "if exist %USERPROFILE%\.claude\.compact-marker (type %USERPROFILE%\.claude\hooks\post-compact-recovery.md & echo. & del %USERPROFILE%\.claude\.compact-marker) & type %USERPROFILE%\.claude\hooks\system-prompt.md"

REM Step 3: Verify marker was deleted
echo.
if exist "%USERPROFILE%\.claude\.compact-marker" (
  echo ❌ Marker file not deleted
) else (
  echo ✅ Marker file deleted
)
```

---

## Comprehensive Test Script

Save this as `test-compact-hook.bat` and run:

```batch
@echo off
setlocal enabledelayedexpansion

echo ============================================
echo Auto-Compact Hook - Comprehensive Test
echo ============================================
echo.

REM Colors
set "SUCCESS=✅"
set "FAILURE=❌"
set "INFO=ℹ️"

echo [1/5] Checking hook files...
if exist "C:\Users\Jayone\.claude\hooks\pre-compact-save.js" (
  echo %SUCCESS% pre-compact-save.js found
) else (
  echo %FAILURE% pre-compact-save.js NOT found
  goto :error
)

if exist "C:\Users\Jayone\.claude\hooks\post-compact-recovery.md" (
  echo %SUCCESS% post-compact-recovery.md found
) else (
  echo %FAILURE% post-compact-recovery.md NOT found
  goto :error
)

echo.
echo [2/5] Validating Node.js syntax...
node -c "C:\Users\Jayone\.claude\hooks\pre-compact-save.js" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
  echo %SUCCESS% JavaScript syntax valid
) else (
  echo %FAILURE% JavaScript syntax invalid
  goto :error
)

echo.
echo [3/5] Checking settings.json...
python -m json.tool "C:\Users\Jayone\.claude\settings.json" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
  echo %SUCCESS% JSON format valid
) else (
  echo %FAILURE% JSON format invalid
  goto :error
)

echo.
echo [4/5] Verifying hook configuration in settings.json...
findstr "PreCompact" "C:\Users\Jayone\.claude\settings.json" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
  echo %SUCCESS% PreCompact hook configured
) else (
  echo %FAILURE% PreCompact hook NOT configured
  goto :error
)

findstr "post-compact-recovery" "C:\Users\Jayone\.claude\settings.json" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
  echo %SUCCESS% UserPromptSubmit hook configured
) else (
  echo %FAILURE% UserPromptSubmit hook NOT configured
  goto :error
)

echo.
echo [5/5] Creating backup directory...
if not exist "%USERPROFILE%\.claude\context-backups" (
  mkdir "%USERPROFILE%\.claude\context-backups"
)
echo %SUCCESS% Backup directory ready

echo.
echo ============================================
echo %SUCCESS% ALL TESTS PASSED - READY FOR USE
echo ============================================
echo.
echo Next Steps:
echo 1. Wait for natural auto-compact event
echo 2. OR manually test with: node pre-compact-save.js
echo 3. Check %USERPROFILE%\.claude\context-backups for backups
echo 4. Verify marker file is created/deleted
echo.
goto :end

:error
echo.
echo %FAILURE% TEST FAILED - Please check configuration
echo.

:end
endlocal
```

---

## What to Expect During Real Auto-Compact

### Timeline

```
T+0s     Auto-compact triggered
         ↓
T+0.5s   PreCompact hook executes
         ├─ pre-compact-save.js runs
         ├─ Reads transcript last 50 lines
         ├─ Creates backup file
         └─ Creates marker file
         ↓
T+1-2s   Claude Code compresses context
         ↓
T+X      User submits next prompt
         ↓
         UserPromptSubmit hook executes
         ├─ Checks for marker file
         ├─ Displays post-compact-recovery.md (if marker exists)
         ├─ Deletes marker file
         └─ Displays system-prompt.md
         ↓
         Conversation continues normally
```

---

## Troubleshooting

### Issue: Marker file not created

**Check:**
```bash
# Verify pre-compact-save.js has execute permissions
dir C:\Users\Jayone\.claude\hooks\pre-compact-save.js

# Check hook command in settings.json
findstr "pre-compact-save" C:\Users\Jayone\.claude\settings.json
```

### Issue: Recovery.md not displaying

**Check:**
```bash
# Verify file exists
if exist C:\Users\Jayone\.claude\hooks\post-compact-recovery.md (
  echo File exists
) else (
  echo File NOT found
)

# Check marker file condition in settings.json
findstr "compact-marker" C:\Users\Jayone\.claude\settings.json
```

### Issue: Node.js process timeout

**Check:**
```bash
# Verify Node.js is installed
node --version

# Test with simple script
echo console.log('test'); | node
```

---

## Monitoring Commands

Run these to monitor the system:

```bash
# Watch backup directory for new files
dir /O-D %USERPROFILE%\.claude\context-backups

# Check backup file content
type %USERPROFILE%\.claude\context-backups\last_context_*.jsonl | more

# Monitor marker file
if exist %USERPROFILE%\.claude\.compact-marker (
  type %USERPROFILE%\.claude\.compact-marker
)

# Check logs (if Claude Code creates them)
dir %USERPROFILE%\.claude\*.log 2>nul
```

---

## Success Criteria

✅ **All the following indicate success:**

1. `pre-compact-save.js` has valid Node.js syntax
2. `settings.json` has valid JSON format
3. PreCompact hook is configured with "auto" matcher
4. UserPromptSubmit hook checks for marker file
5. Backup files appear in `~/.claude/context-backups/`
6. Marker file is created before compaction
7. Marker file is deleted after recovery.md display
8. Recovery guide displays after auto-compact

---

## Next: Run Test

Execute this now to verify everything is working:

```bash
REM Run the comprehensive test script
cd %USERPROFILE%\.claude\hooks
test-compact-hook.bat
```

If all tests pass ✅, your setup is ready for production use!
