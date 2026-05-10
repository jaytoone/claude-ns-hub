# Orchestrator System - RLM + Reflective Hook

## 개요

Claude Code Hook에 **재귀적 계획 수정(Reflective RLM)**을 도입한 시스템입니다. 기존 `analyze-complexity.ps1` 기능을 완전히 호환하면서, 향후 Block-based 실행과 LLM 하이브리드 평가를 지원합니다.

## 구조

```
C:\Users\Jayone\.claude\
├── settings.json                 # Hook 설정 (orchestrator.ps1 호출)
├── system-prompt.md              # 핵심 Instructions (변경 없음)
├── hooks/
│   ├── orchestrator.ps1          # 메인 엔트리 포인트
│   ├── auto-dev-context.md       # Auto-dev 컨텍스트 (변경 없음)
│   ├── blocks/
│   │   ├── 00-analyze.ps1        # LLM 하이브리드 복잡도 평가
│   │   ├── 01-research.ps1       # 파일 탐색 (Placeholder)
│   │   ├── 02-design.ps1         # 계획 수립 (Placeholder)
│   │   ├── 03-verify.ps1         # 계획 검증 (Placeholder)
│   │   └── 04-phase-reflect.ps1  # 전체 검토 (Placeholder)
│   ├── ROLLBACK.md               # 롤백 가이드
│   └── README-ORCHESTRATOR.md    # 이 문서
├── orchestrator-states/          # State persistence 저장소
└── backup-20260109-162157/       # 백업 (롤백용)
```

## 주요 기능

### 1. 기존 기능 완전 호환
- ✅ 영어 키워드 기반 복잡도 분석 (HIGH/MEDIUM/LOW)
- ✅ MEDIUM/HIGH 복잡도 → auto-dev-context.md 자동 주입
- ✅ 기존 `analyze-complexity.ps1`과 동일한 출력 형식

### 2. 새로운 기능 (Opt-in)
- 🆕 LLM 하이브리드 평가 (키워드 신뢰도 < 0.7일 때)
- 🆕 State persistence (체크포인트 파일)
- 🆕 Block-based 실행 준비 (향후 확장)

### 3. 안전성
- ✅ 백업 자동 생성 (`backup-20260109-162157`)
- ✅ 롤백 가이드 제공 (`ROLLBACK.md`)
- ✅ Fallback 로직 (Block 00 실패 시 키워드 기반 결과 사용)

## 사용 방법

### 기본 모드 (Default)

설정 없이 바로 사용 가능. 기존 `analyze-complexity.ps1`과 동일하게 동작합니다.

```bash
# Claude Code 사용 시 자동 실행
# 예: "add a new button"
# 출력:
# [COMPLEXITY: MEDIUM]
# [KEYWORD_CONFIDENCE: 0.8]
# [TRIGGER: AUTO_DEV_PIPELINE]
# + auto-dev-context.md 내용
```

### 향상 모드 (Enhanced - 실험적)

환경 변수로 활성화:

```powershell
$env:ENABLE_RLM_BLOCKS = "true"
```

**기능:**
- Block 00 호출 (키워드 신뢰도 < 0.7일 때)
- State persistence 활성화
- 향후 Block 01-04 실행 준비

**주의:** Block 00은 현재 한글 출력 오류가 있으나, fallback이 정상 작동합니다.

## 테스트 결과

### Test 1: MEDIUM 복잡도
```
프롬프트: "add a new button to the login page"
결과: ✅ MEDIUM, 0.8 confidence, auto-dev 주입 성공
```

### Test 2: HIGH 복잡도
```
프롬프트: "implement WebSocket real-time notifications"
결과: ✅ HIGH, 0.9 confidence, auto-dev 주입 성공
```

### Test 3: LOW 복잡도
```
프롬프트: "what is the current database schema"
결과: ✅ LOW, 0.85 confidence, auto-dev 주입 안됨 (정상)
```

### Test 4: 향상 모드 (ENABLE_RLM_BLOCKS=true)
```
프롬프트: "WebSocket integration"
결과: ⚠️ MEDIUM, 0.5 confidence, Block 00 호출 (오류 발생 → fallback 작동)
```

## 키워드 매핑

### HIGH 복잡도
- `implement`, `develop`, `architecture`, `pipeline`, `system`, `integrate`, `design`, `build`

### MEDIUM 복잡도
- `add`, `modify`, `change`, `update`, `refactor`, `improve`, `fix`, `enhance`, `optimize`

### LOW 복잡도
- `what`, `explain`, `tell`, `find`, `check`, `show`, `where`, `which`, `how`, `list`

## 다음 단계

### Phase 2: Block 01-04 구현
1. **Block 01 (Research)**: Glob/Grep 기반 파일 탐색
2. **Block 02 (Design)**: 상세 구현 계획 생성
3. **Block 03 (Verify)**: 계획 일관성 검증
4. **Block 04 (Phase-Reflect)**: 전체 품질 검토

### Phase 3: LLM 하이브리드 개선
- Block 00 한글 출력 오류 수정
- LLM 평가 결과를 다음 Block에 전달
- Retry logic 개선

### Phase 4: Full RLM + Reflective 활성화
- Block-level Reflection (각 블록 자체 검증)
- Phase-level Reflection (전체 일관성 검토)
- Selective Rollback (실패한 블록만 재실행)

## 문제 해결

### Block 00 오류
**증상:** Enhanced mode에서 Block 00 호출 시 오류
**해결:** Fallback이 자동 작동하여 키워드 기반 결과 사용
**상태:** 정상 동작 (향후 수정 예정)

### Auto-dev 주입 안됨
**원인:** 복잡도가 LOW로 판정됨
**해결:** 프롬프트에 MEDIUM/HIGH 키워드 포함 (예: "add", "implement")

### 롤백이 필요한 경우
`ROLLBACK.md` 참조

## 참조 문서

- **Spec 문서**: `D:\Project\VIDraft\HugwartsBanana\docs\specs\rlm-reflective-hook-system-spec.md`
- **백업**: `C:\Users\Jayone\.claude\backup-20260109-162157`
- **롤백 가이드**: `C:\Users\Jayone\.claude\hooks\ROLLBACK.md`

## 버전 이력

- **v1.0.0** (2026-01-09): 초기 릴리스
  - orchestrator.ps1 생성
  - Block 00-04 기본 구조
  - 기존 analyze-complexity.ps1 완전 호환
  - State persistence 준비
  - 백업 및 롤백 시스템
