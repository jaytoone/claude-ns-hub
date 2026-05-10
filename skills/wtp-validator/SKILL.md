---
name: wtp-validator
description: "WTP orchestration SCAFFOLD — 6-condition diagnosis + experiment design + /live loop integration. IMPORTANT: for standalone WTP validation analysis, prefer dispatching to the `biz-wtp-validator` Agent directly. This skill owns the end-to-end harness (PHASE 0-7) and dev build trigger (PHASE 6)."
---

<!-- CLASSIFICATION: skill (orchestration scaffold)
     Overlap: `biz-wtp-validator` (Agent) covers the same WTP domain.
     Division of responsibility:
       - biz-wtp-validator (Agent): isolated WTP analysis, standalone dispatch
       - wtp-validator (Skill): full harness with /live loop + PHASE 6 dev trigger
     When to use this skill vs the agent:
       - Use Agent(biz-wtp-validator) for: one-shot WTP diagnosis
       - Use /wtp-validator for: full A-to-Z loop with dev build trigger
-->

# WTP Validator — A-to-Z Harness

## Trigger
- `/wtp-validator [idea]`
- "WTP 검증해줘", "이 아이디어 검증", "비즈니스 아이디어 WTP"
- /live loop에서 자동 호출 (PHASE 6 dev trigger 포함)

---

## PROFESSIONAL WTP KNOWLEDGE BASE (알파)

### WTP 과학 핵심 원리 (항상 적용)

**1. Reference Price Effect (기준가격 효과)**
- 고객은 절대가격이 아닌 "기준 대비 비교"로 판단
- 처방: 경쟁사 가격 또는 현재 비용(시간×시급)을 먼저 제시하면 WTP 상승
- 예: "프리랜서 월 150만원 vs 우리 서비스 29,000원"

**2. Loss Aversion Framing (손실 회피 프레이밍)**
- "얻는 것" 보다 "잃는 것"이 2.5배 더 강한 구매 동기
- 처방: "이 기능이 없으면 X를 놓칩니다" 프레임이 "이 기능으로 X를 얻습니다"보다 효과적

**3. Decoy Effect (미끼 효과)**
- 3개 가격 옵션 제시 시 중간 옵션 선택률 극대화
- 처방: Free / Standard($29) / Pro($79) 구조에서 Standard가 최대 판매

**4. Endowment Effect (소유 효과)**
- 일단 써보면 WTP가 올라감 (보유 효과)
- 처방: 무료 체험 → 유료 전환이 cold pitch보다 WTP 3-5x 높음

**5. Social Proof + FOMO**
- "XX명이 사용 중" / "이번 주 마감" → 구매 전환율 상승
- 처방: 대기자 리스트, 베타 자리 제한, 실사용자 이름 노출

**6. Van Westendorp PSM (Price Sensitivity Meter)**
4문항으로 수용 가능 가격대 산출:
- Q1: "너무 비싸서 안 사겠다" → 상한선
- Q2: "비싸지만 고려해볼 만하다" → 수용 상한
- Q3: "적정하다" → 최적 가격
- Q4: "너무 싸서 품질이 의심된다" → 하한선
→ 교차점: Acceptable Price Range (APR) + Optimal Price Point (OPP)

**7. Gabor-Granger Method**
- 직접 가격 노출 후 "이 가격이면 사겠습니까?" Y/N
- N=20으로 수요 곡선 산출 가능
- 가격 포인트: 9,000 / 19,000 / 29,000 / 49,000 / 79,000

**8. Pre-sale Signal (가장 강한 WTP 신호)**
- "지금 결제 → 30일 후 납품" = 진짜 WTP
- 설문 100명 > 결제 1건 → 결제 1건이 더 강한 증거
- 처방: 아임포트/토스페이먼츠로 선결제 받기

---

## PHASE 0 — INTAKE

```
IDEA:             [one-line business idea]
STAGE:            [idea / prototype / early-revenue / scaling]
CURRENT_ACTIONS:  [지금까지 한 것]
TARGET_CUSTOMER:  [role + company type + size]
PRICE_HYPOTHESIS: [예상 가격대]
BLOCKERS:         [현재 막히는 것]
```

미입력 필드 confidence < 0.7 → 질문 1개씩

---

## PHASE 1 — 6-CONDITION DIAGNOSIS

각 조건 1-5점 채점. 근거 없으면 자동 -1점.

### Condition 1: 시장 (Market Validity)
- 타겟 고객 정의: role + company type + size 명시 여부
- 의사결정자 직접 도달 여부 (CS팀 = 게이트키퍼 = -2점)
- 직접 인터뷰 건수 (0건 = 2점 이하)
- TAM > 목표 매출 10x 확인 여부

| 점수 | 기준 |
|------|------|
| 5 | 의사결정자 식별 + 5건 인터뷰 + TAM 확인 |
| 3 | 타겟 정의 + 게이트키퍼 리스크 + 인터뷰 1-2건 |
| 1 | "X가 필요한 모든 사람" + 인터뷰 0건 |

### Condition 2: 채널 (Response Collection Channel)
- 응답률: 이메일 단방향 = 낮음, 답장/LinkedIn/콜 = 높음
- 정성 신호 수집 여부 (왜 클릭했는지/안 했는지)
- 채널 다양성: 단일 채널 = 취약

| 점수 | 기준 |
|------|------|
| 5 | 멀티채널 + 정성+정량 + 응답률 >20% |
| 3 | 단일 채널 (이메일) + 정량만 |
| 1 | 이메일 단방향 + 답장 없음 + 트래킹 픽셀만 |

채널 대안: LinkedIn DM / 커뮤니티 / 콜드콜 / 커뮤니티 포스팅 / 컨시어지

### Condition 3: 아이템 (Item Clarity & Demo-ability)
- 결과물 미리보기 존재 여부 (샘플/데모/목업)
- 30초 이내 이해 가능 여부
- 고객이 자가 평가 가능 여부

| 점수 | 기준 |
|------|------|
| 5 | 데모/샘플 존재 + 고객 자가 평가 가능 |
| 3 | 설명 존재 + 미리보기 없음 |
| 1 | 추상적 기능 주장 + 증거 없음 |

### Condition 4: 대안 (Alternative Mapping)
- 고객이 지금 이 문제를 어떻게 해결하는가 파악 여부
- "vs [경쟁사/방식]" 명시적 포지셔닝 여부
- 고객이 대안의 열등함에 동의 여부

| 점수 | 기준 |
|------|------|
| 5 | 구체적 대안 3개 이상 명시 + 고객 검증 |
| 3 | 대안 추정 + 차별화 자가 선언 |
| 1 | "대안 없음" 주장 또는 조사 미실시 |

대안 맵핑 필수: 수동/DIY / 기존 도구 / 에이전시/프리랜서 / 문제 무시

### Condition 5: 타이밍 (Purchase Timing Alignment)
- 구매 트리거 이벤트 존재 여부
- 예산 사이클 정렬 여부
- 지금 사지 않으면 어떻게 되는가 (긴박성)

| 점수 | 기준 |
|------|------|
| 5 | 트리거 이벤트 확인 + 예산 사이클 정렬 + 긴박성 검증 |
| 3 | 트리거 없음 + "준비되면 살 것" 가정 |
| 1 | 랜덤 발송 + 긴박성 없음 |

긴박성 레버: 예산 마감 / 법적 데드라인 / 경쟁 위협 / 시즌 피크 / 자리 제한

### Condition 6: 신뢰 (Trust & Credibility)
- 발신자 신원 명확성 (익명 = 0점)
- 소셜 증거 존재 여부 (레퍼런스/케이스 스터디)
- 리스크 리버설 존재 여부 (무료 체험/환불 보장)

| 점수 | 기준 |
|------|------|
| 5 | 실명 레퍼런스 + 케이스 스터디 + 리스크 리버설 |
| 3 | 자격 주장 + 미검증 + 레퍼런스 없음 |
| 1 | 익명 발신 + 이전 실적 없음 + 리스크 리버설 없음 |

---

## PHASE 2 — SCORING TABLE

```
CONDITION          SCORE   STATUS      BLOCKER / 근거
시장 (Market)       X/5    🟢/🟡/🔴    [구체적 갭]
채널 (Channel)      X/5    🟢/🟡/🔴    [구체적 갭]
아이템 (Item)        X/5    🟢/🟡/🔴    [구체적 갭]
대안 (Alternative)  X/5    🟢/🟡/🔴    [구체적 갭]
타이밍 (Timing)     X/5    🟢/🟡/🔴    [구체적 갭]
신뢰 (Trust)        X/5    🟢/🟡/🔴    [구체적 갭]

TOTAL: XX/30
WTP_READINESS: NOT_READY(<15) / PARTIAL(15-22) / READY(23+)
ESTIMATED_SIGNAL_WEEKS: N주
```

🔴 = 즉시 중단 후 픽스 → 다른 조건 진행 전 필수

---

## PHASE 3 — EXPERIMENT DESIGN

각 갭(점수 < 4)에 대해 실험 1개 처방:

```
CONDITION:        [조건명]
WTP_PRINCIPLE:    [적용할 WTP 과학 원리]
HYPOTHESIS:       "만약 [액션]하면, [고객]이 [행동]할 것이며, [조건]이 충족됨을 증명"
EXPERIMENT:       [1주 내 실행 가능한 구체적 행동]
CHANNEL:          [실행 채널]
SAMPLE_SIZE:      [최소 N]
SUCCESS_METRIC:   [검증 기준]
FAILURE_METRIC:   [피벗 트리거]
TIMELINE:         [일수]
COST:             [시간 + 비용]
```

### 조건별 실험 메뉴

**시장 fix**: 고객 발견 콜 5건 (스크립트: "지금 이 문제 어떻게 해결? 얼마 지불? 누가 결정?")
→ 성공: 3/5 확인 → 활성 통증 + 예산 있음

**채널 fix**: 이메일 vs LinkedIn DM vs 커뮤니티 포스팅 A/B (동일 ICP)
→ 성공: 채널 하나가 >15% 응답률

**아이템 fix**: 구체적 샘플 1개 제작 (리포트/데모/목업) → 5명에게 발송
→ 성공: 3/5 "우리 회사에도 이거 원해요"

**대안 fix**: "vs [대안]" 프레이밍 추가 + "지금 어떻게 하세요?" 질문 삽입
→ 성공: 3/5 "당신 방식이 더 낫네요" 확인

**타이밍 fix**: 트리거 이벤트 (예산 마감 2주 전) 타이밍으로 발송
→ 성공: 베이스라인 대비 2x 응답률

**신뢰 fix**: 레퍼런스 1개 추가 또는 무료 파일럿 1건 제공
→ 성공: 레퍼런스 검증 가능 + 파일럿 수락

---

## PHASE 4 — WTP MEASUREMENT PROTOCOL

모든 조건 ≥ 3 달성 후 공식 WTP 측정:

### 단계별 방법 선택

| 단계 | 방법 | 최소 N | 기간 | 신뢰도 |
|------|------|--------|------|--------|
| 아이디어 | Fake Door (가격 클릭) | 20 방문자 | 1주 | 낮음 |
| 프로토타입 | Van Westendorp PSM | 20 응답 | 1주 | 중간 |
| 초기 | Pre-sale / LOI | 5 결제 | 2주 | 높음 |
| 매출 | Gabor-Granger / Conjoint | 50 응답 | 2주 | 매우 높음 |

### Van Westendorp 4문항 (인터뷰/설문)
1. "이 가격이라면 너무 비싸서 안 사겠다" → [가격]
2. "이 가격이라면 비싸지만 고려해보겠다" → [가격]
3. "이 가격이라면 적정하다고 생각한다" → [가격]
4. "이 가격이라면 품질이 의심된다" → [가격]
→ APR 교차점 산출 → Optimal Price Point 결정

### Gabor-Granger 실행
가격 포인트 순서: 49,000 → 29,000 → 19,000 → 9,000 → 4,900
각 포인트에서 "이 가격이면 구매하시겠습니까?" Y/N
→ 수요 곡선: 응답률(%) × 가격 = 최대 매출 포인트

### Pre-sale (가장 강한 신호)
- 요청: 신용카드 또는 인보이스 커밋먼트
- "지금 결제 → 30일 후 납품" 형태
- 결제 1건 = 설문 100건 이상의 WTP 증거

---

## PHASE 5 — TRACKING & ITERATION

### 주간 리뷰 템플릿
```
WEEK: N
EXPERIMENTS_RUN: [목록]
SIGNAL_COLLECTED: [정량 결과]
CONDITION_UPDATES: [변경된 조건 점수]
WTP_PRINCIPLE_APPLIED: [적용한 원리와 효과]
PIVOT_TRIGGERS: [레드 플래그]
NEXT_WEEK_PRIORITY: [1순위 실험]
```

### Go/No-Go 기준
- **GO (개발 진입)**: 전 조건 ≥ 4 + Pre-sale 또는 Gabor-Granger 가격 확정
- **PIVOT_ITEM**: 조건 1/2/6 OK + 3/4 실패 → 아이템 변경
- **PIVOT_MARKET**: 아이템 검증 + 조건 1/5 실패 → 타겟 변경
- **STOP**: 조건 3개 이상 4주 후에도 1-2점 → 아이디어 포기

---

## PHASE 6 — PLATFORM BUILD (개발 트리거)

### 진입 조건
전 조건 ≥ 4 AND (Pre-sale 1건 이상 OR Gabor-Granger 가격 확정)

### 개발 명령 시퀀스 (자동 실행)

**Step 1: 아웃리치 파이프라인**
```
dev-deep-executor 호출:
- 이메일 발송 자동화 (Brevo/Gmail SMTP)
- LinkedIn DM 템플릿 생성기
- 발송 스케줄러 (트리거 이벤트 기반)
- 답장 모니터링 대시보드
```

**Step 2: 랜딩 페이지**
```
frontend-design 호출:
- Fake Door → 실제 결제 페이지 전환
- Van Westendorp PSM 인터랙티브 설문
- Pre-sale 체크아웃 (Paddle Checkout)
- WTP 원리 적용: 기준가격 표시 + 손실 회피 카피 + 사회 증거
```

**Step 3: 트래킹 대시보드**
```
dev-executor 호출:
- 6조건별 실시간 점수 트래킹
- 실험 결과 누적 (주간 리뷰 자동화)
- Gabor-Granger 수요 곡선 시각화
- 채널별 응답률 비교
- Cohort별 WTP 분포
```

**Step 4: 팔로업 시퀀스**
```
dev-executor 호출:
- D+3 / D+7 / D+14 자동 팔로업
- 조건별 메시지 분기 (아이템 관심 vs 가격 관심 vs 타이밍 관심)
- 답장 분류 → 조건 점수 자동 업데이트
```

**Step 5: CRM 통합**
```
dev-executor 호출:
- 고객 반응 조건별 태깅
- 인터뷰 스케줄러 (Calendly 연동)
- WTP 점수 이력 관리
```

### 기술 스택 (WTP 프로젝트 기준)
```
Frontend: Next.js + Tailwind (wtp-dashboard/ 내 새 페이지로 추가)
Backend:  Next.js API routes
DB:       Supabase (기존 연결 재사용)
Email:    Brevo (Kool) / Gmail (CL) 기존 SMTP
Payment:  Paddle (Pre-sale용, 글로벌 결제 + 세금 처리 포함)
Analytics: 기존 트래킹 픽셀 확장
```

---

## PHASE 7 — /live 통합

### 루프 훅

**SessionStart 시 자동 실행:**
```
1. 현재 실험 상태 로드 (wtp-dashboard DB 조회)
2. 전주 대비 조건 점수 변화 리포트
3. 이번 주 최우선 실험 1개 결정
4. PHASE 6 진입 조건 체크
```

**루프 내 반복 작업:**
```
매 이터레이션:
- 새 아웃리치 응답 분류 → 조건 점수 업데이트
- 실험 성공/실패 판정
- 다음 실험 처방
- PHASE 5 주간 리뷰 자동 생성
```

**수렴 조건 (루프 종료):**
```
OR:
- 전 조건 ≥ 4 + Pre-sale 완료 → PHASE 6 진입
- STOP 기준 충족 → 아이디어 폐기 리포트
- 사용자 명시적 중단
```

**에피소드 메모리 저장 형식:**
```json
{
  "idea": "...",
  "week": N,
  "condition_scores": { "market": X, "channel": X, ... },
  "experiments_run": [...],
  "wtp_signal": "...",
  "next_action": "..."
}
```

---

## ANTI-PATTERNS (즉시 중단)

- 아이템 미시연 상태에서 WTP 측정 → 아이템 먼저
- B2B 엔터프라이즈인데 이메일만 → LinkedIn/콜 추가
- 의사결정자 미도달 → 타겟 재구성
- "대안 없음" 주장 → 대안 3개 먼저 열거
- 신뢰 없이 발송 → 레퍼런스 1개 최소
- "고객이 원할 것 같다" = 증거 아님 → -1점 자동 적용
- 설문 응답 = WTP 증거 아님 → Pre-sale 또는 Gabor-Granger로 교체

---

## OUTPUT FORMAT

```
## WTP Validation Report — [아이디어]
Date: YYYY-MM-DD | Stage: [단계]

### 6-Condition Scores
[표]

### Applied WTP Principles
[이번 진단에 적용된 원리]

### Critical Blockers
[🔴 조건 + 즉시 처방]

### This Week's Experiment
[단일 최우선 실험 + 실험 설계]

### WTP Readiness: [NOT_READY / PARTIAL / READY]
### Dev Build Ready: [YES / NO / PENDING]
### Estimated signal: [N주]
```
