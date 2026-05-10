# analyze-complexity.ps1 제거 안내

**제거 일자:** 2026-01-10
**버전:** v1.6.8

## 제거 이유

PowerShell 기반 키워드 매칭 복잡도 분석 방식을 **Claude 기반 의미론적 분석**으로 전환하기 위해 제거되었습니다.

## 기존 방식의 한계

### analyze-complexity.ps1 (제거됨)
```powershell
# 영어 키워드 패턴 매칭
$HighKeywords = "implement|develop|architecture|..."
$MediumKeywords = "add|modify|change|..."
$LowKeywords = "what|explain|tell|..."

if ($UserPrompt -match $HighKeywords) {
    $Complexity = "HIGH"
}
```

**문제점:**
- ❌ 정확도: 영어 60-70%, 한글 40-50%
- ❌ 컨텍스트 무시: "explain how to implement" → HIGH (실제 LOW)
- ❌ 한글 미지원: "구현해", "개발해" 등 매칭 불가
- ❌ 오분류: "fix minor typo" → MEDIUM (실제 LOW)

## 새로운 방식 (Claude 기반)

### system-prompt.md (Claude 판단)
```markdown
## 복잡도 선언 (MANDATORY - Claude 기반 판단)

### 복잡도 판단 기준
- LOW: 정보 조회, 1-2줄 수정
- MEDIUM: 1-3개 파일, 버그 수정
- HIGH: 새 기능, 5개 이상 파일
```

**장점:**
- ✅ 정확도: 95%+ (프롬프트 의미 이해)
- ✅ 한글 지원: 완벽
- ✅ 컨텍스트 고려: "설명해 - 구현 방법" → LOW (정확)
- ✅ 토큰 증가: +50-100 토큰 (미미한 수준)

## 변경 사항

### settings.json
```json
// Before
"hooks": [
  {
    "command": "cat .../system-prompt.md"
  },
  {
    "command": "powershell ... analyze-complexity.ps1"  // 제거됨
  }
]

// After
"hooks": [
  {
    "command": "cat .../hooks/system-prompt.md"  // 경로 변경
  }
]
```

### system-prompt.md
- 위치 변경: `.claude/system-prompt.md` → `.claude/hooks/system-prompt.md`
- 내용 추가: Claude 기반 복잡도 판단 가이드

## 파일 보관

`analyze-complexity.ps1` 파일은 참고용으로 보관되었습니다.
- 위치: `C:\Users\Jayone\.claude\hooks\analyze-complexity.ps1`
- 상태: Hook에서 제거됨 (실행 안됨)
- 용도: 필요 시 참고용

## Rollback 방법

문제 발생 시 복구:

1. **settings.json 복구**
   ```json
   "hooks": [
     {
       "command": "cat /c/Users/Jayone/.claude/hooks/system-prompt.md"
     },
     {
       "command": "powershell -ExecutionPolicy Bypass -File C:\\Users\\Jayone\\.claude\\hooks\\analyze-complexity.ps1"
     }
   ]
   ```

2. **system-prompt.md에서 복잡도 가이드 제거** (선택사항)

## 관련 문서

- Quick Spec: `docs/specs/claude-based-complexity-spec.md`
- RLM v2: `docs/specs/rlm-v2-implementation-spec.md` (예정)
- Auto-dev Context: `.claude/hooks/auto-dev-context.md`
