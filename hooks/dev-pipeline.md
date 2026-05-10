# Development Pipeline (PDE + RLM v2 통합)

**적용 조건**: 복잡도 MEDIUM/HIGH 선언 시 자동 로드
**목적**: 충분한 질의응답 → 완전한 Requirements → 긴 호흡의 자동 개발

---

## 🧠 통합 전문가 패널 (Single Source of Truth)

### Core Team (항상 참여)

| 전문가 | 역할 | 핵심 질문 |
|--------|------|-----------|
| 🏗️ Architect | 설계, 구조, 확장성 | "기존 시스템 어느 부분에 영향?" |
| 🧪 QA | 테스트, edge case, 검증 | "실패 시 어떻게 처리?" |
| 🔒 Security | 인증, 권한, 취약점 | "인증/권한 필요한 부분?" |

### Extended Team (작업 유형별 선택)

| 전문가 | 트리거 조건 | 핵심 질문 |
|--------|------------|-----------|
| 🎯 PM | NEW_FEATURE, UI_CHANGE | "핵심 사용자 가치?" |
| 🎨 UX | UI_CHANGE | "사용자 인터랙션 흐름?" |
| 💾 DBA | DATA_CHANGE | "마이그레이션 전략?" |
| ⚡ Performance | 성능 관련 요구사항 | "병목 예상 지점?" |
| 🚀 DevOps | INFRA, 마이그레이션 | "배포 시 특별 절차?" |

### 작업 유형 분류

| 유형 | 설명 | 활성 전문가 |
|------|------|------------|
| `NEW_FEATURE` | 신규 기능 구현 | Core + PM, (Security) |
| `BUG_FIX` | 버그 수정 | Core |
| `REFACTOR` | 리팩토링 | Core |
| `INTEGRATION` | 외부 서비스/API 통합 | Core + DevOps |
| `UI_CHANGE` | UI/UX 변경 | Core + PM, UX |
| `DATA_CHANGE` | DB 스키마/데이터 변경 | Core + DBA |
| `INFRA` | 배포/인프라 관련 | Core + DevOps |

---

## Phase 1: PDE (Pre-Development Elicitation)

### Step 1: 초기 분석 (자동)

사용자 요청 수신 즉시:
1. 작업 유형 분류 (위 표 참조)
2. 활성 전문가 결정
3. 핵심 질문 준비

### Step 2: 질의응답 (AskUserQuestion)

**규칙:**
- 라운드당 최대 4개 질문
- 최대 3라운드 (적응형)
- Core Team 질문 우선

**라운드 진행:**
```
라운드 1: Core Team 핵심 질문 (Architect, QA, Security)
라운드 2: Extended Team + 불명확 부분 후속 질문
라운드 3: 최종 확인 (여전히 모호한 부분)
```

**종료 조건:**
- 모든 핵심 항목 명확
- 3라운드 완료
- 사용자 "ㄱㄱ" / "진행해" 응답

### Step 3: Requirements 정제 (Self-Refine)

```
[Draft] 수집 정보로 Requirements 초안
     ↓
[Critique] 체크리스트 검토
  □ 기능 범위 명확?
  □ 기술 제약 정의?
  □ Edge cases 식별?
  □ 성공 기준 명확?
  □ 제외 범위 정의?
     ↓
[Refine] 누락/모호 부분 보완
```

### Step 4: 사용자 승인

```markdown
## 📋 Requirements Summary

### 기능 요약
[1-2문장]

### 상세 요구사항
- [ ] 요구사항 1
- [ ] 요구사항 2

### 기술 제약
- 제약 1

### Edge Cases
| 케이스 | 처리 |
|--------|------|
| 케이스1 | 처리1 |

### 성공 기준
- [ ] 기준 1

### 제외 범위
- 이번에 안 함 1
```

→ 승인 시 Phase 2로 진행

---

## Phase 2: RLM v2 (Reflective LLM)

### Step 1: SPEC 문서 작성

**내부 시뮬레이션 (Expert Panel):**
```
[Expert Panel - Internal]
🏗️ Architect: [설계 구조 제안]
🔒 Security: [보안 체크포인트]
⚡ Performance: [성능 고려사항]
🚀 DevOps: [배포 주의사항]
→ 통합 SPEC 작성
```

**출력:** `docs/specs/[task-name]-spec.md`

### Step 2: 블록 분해 (TodoWrite)

**규칙:**
- 5-10개 독립 블록
- 블록당 30분 이내
- 동사-명사 형식 (예: "구현-API", "검증-테스트")

**Expert Block Proposals (내부):**
```
🏗️ Architect: "설계-인터페이스", "설계-데이터모델"
🔒 Security: "설계-RLS정책", "검증-입력검증"
⚡ Performance: "최적화-인덱스"
🚀 DevOps: "작성-마이그레이션", "설정-환경변수"
🧪 QA: "검증-qa-expert" (필수)
→ 통합 후 최종 블록 리스트
```

**필수 블록 (강제):**
```
구현 블록들...
└── 검증-qa-expert (필수) ← Playwright E2E 포함
문서화 블록
```

### Step 3: 블록별 재귀 실행

각 블록:
1. repomix MCP로 필요 정보 수집
2. 구현
3. Playwright E2E 검증 (Backend API + Frontend UI)
4. Reflection 체크리스트

**Reflection Checklist (각 블록 후):**
```
□ 목표 100% 달성?
□ 예상치 못한 문제?
□ 다음 블록 영향도?
□ 계획 수정 필요?
□ Playwright 검증 완료? (Backend/Frontend 모두)

→ 필요 시 TodoWrite 즉시 업데이트
```

**복잡한 블록 시 재귀:**
```typescript
Task({
  subagent_type: "general-purpose",
  description: "[블록명] 구현",
  prompt: `RLM 프로세스 적용:
    1. TodoWrite로 하위 블록 분해
    2. 각 블록 순서대로 실행
    3. 각 블록 후 Reflection
    4. 완료 후 상위에 보고`
})
```

### Step 4: Final Reflection

```
[Final Reflection]
□ 사용자 요청 100% 달성?
□ 누락된 요구사항?
□ Playwright E2E 전체 완료?
  - Backend API: 브라우저 fetch 검증
  - Frontend UI: 인터랙션 검증
  - 콘솔/네트워크 에러 확인

→ 미완료 시 추가 블록 실행
```

---

## Phase 3: 배포 승인

**제공 정보:**
- 📋 변경 파일 목록
- 🧪 테스트 결과
- 📊 영향 범위 분석

**승인 시 자동 커밋:**
```bash
git add . && git commit -F commit_tree.txt || true
```

---

## 자동 복구 규칙

**막힘 발생 시:**
1. 에러 분석
2. 해결 시도
3. 재실행
4. 3회 실패 시 사용자 보고

---

## 체크리스트: Pipeline 완료 조건

```
□ PDE 완료 (Requirements 확정)
□ SPEC 문서 작성
□ 모든 블록 실행 + Reflection
□ Playwright E2E 전체 통과
□ Quality Gates 통과
□ 사용자 배포 승인
```
