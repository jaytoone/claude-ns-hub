# Rollback Guide - Orchestrator System

## 백업 정보

**백업 위치:** `C:\Users\Jayone\.claude\backup-20260109-162157`

**백업 파일:**
- `settings.json` - 기존 hook 설정
- `hooks/analyze-complexity.ps1` - 기존 복잡도 분석 스크립트
- `hooks/auto-dev-context.md` - Auto-dev 컨텍스트 (변경 없음)
- `hooks/README.md` - 기존 문서

## 롤백 방법

### Option 1: 빠른 롤백 (PowerShell 스크립트)

```powershell
# 백업에서 복원
$backupDir = "C:\Users\Jayone\.claude\backup-20260109-162157"

Copy-Item "$backupDir\settings.json" "C:\Users\Jayone\.claude\" -Force
Copy-Item "$backupDir\hooks\analyze-complexity.ps1" "C:\Users\Jayone\.claude\hooks\" -Force

Write-Host "Rollback complete!" -ForegroundColor Green
```

### Option 2: 수동 롤백

1. `settings.json` 수정:
   ```json
   {
     "hooks": {
       "UserPromptSubmit": [
         {
           "matcher": "",
           "hooks": [
             {
               "type": "command",
               "command": "cat /c/Users/Jayone/.claude/system-prompt.md"
             },
             {
               "type": "command",
               "command": "powershell -ExecutionPolicy Bypass -File C:\\Users\\Jayone\\.claude\\hooks\\analyze-complexity.ps1"
             }
           ]
         }
       ]
     }
   }
   ```

2. 백업에서 `analyze-complexity.ps1` 복사:
   ```powershell
   Copy-Item "C:\Users\Jayone\.claude\backup-20260109-162157\hooks\analyze-complexity.ps1" "C:\Users\Jayone\.claude\hooks\" -Force
   ```

## 롤백 후 확인

```powershell
# 1. settings.json 확인
Get-Content "C:\Users\Jayone\.claude\settings.json" | Select-String "analyze-complexity"

# 2. analyze-complexity.ps1 존재 확인
Test-Path "C:\Users\Jayone\.claude\hooks\analyze-complexity.ps1"
```

## 새 파일 제거 (선택사항)

롤백 후 새로 생성된 파일을 제거하려면:

```powershell
# orchestrator.ps1 제거
Remove-Item "C:\Users\Jayone\.claude\hooks\orchestrator.ps1" -Force

# blocks 디렉토리 제거
Remove-Item "C:\Users\Jayone\.claude\hooks\blocks" -Recurse -Force

# state 디렉토리 제거 (선택)
Remove-Item "$HOME\.claude\orchestrator-states" -Recurse -Force
```

## 문제 해결

### 롤백 후에도 문제가 있다면:

1. Claude Code 재시작
2. 캐시 클리어:
   ```powershell
   Remove-Item "$HOME\.claude\cache" -Recurse -Force -ErrorAction SilentlyContinue
   ```
3. settings.json 구문 검증:
   ```powershell
   Get-Content "C:\Users\Jayone\.claude\settings.json" | ConvertFrom-Json
   ```

## 지원

문제가 지속되면 백업 디렉토리의 원본 파일을 확인하고 수동으로 복원하세요.
