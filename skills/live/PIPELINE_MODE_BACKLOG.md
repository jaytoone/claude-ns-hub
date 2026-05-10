---
name: pipeline-mode-backlog
type: backlog
status: pending
date: 2026-04-01
---

# Pipeline Mode — Multi-Domain Sequential Chaining (보류)

## 개요

omc-live / omc-live-inf에서 비즈니스 도메인 1차 수렴 결과를 기반으로
코드 작업 2차 자율 수행을 지원하는 "Pipeline Mode" 설계.

## 동기

현재 DISPATCH 계층은 iter별 단일 도메인 분류만 지원.
`business → DELEGATE → biz-autopilot` 수렴 후,
그 결과를 input으로 `code → AUTOPILOT → omc-autopilot`을 자동 트리거하는
명시적 도메인 체인 메커니즘이 없음.

## 원하는 동작

```
/live "HarnessOS GTM 전략 수립 → 랜딩 페이지 구현"

Phase A [domain:business]: biz-autopilot
  → CONVERGED → output: GTM전략.md, 카피, 채널 계획

Phase B [domain:code]: omc-autopilot
  → input: Phase A output 자동 주입 (context_primer)
  → dev-executor 랜딩 페이지 구현
  → CONVERGED
```

## 필요한 설계 요소

1. `pipeline_goals` 파라미터:
   ```
   pipeline_goals: [
     "GTM 전략 수립 [domain:business]",
     "랜딩 페이지 구현 [domain:code]"
   ]
   ```

2. Phase 전환 트리거:
   - Phase A CONVERGED_SUCCESS → Phase B 자동 시작
   - `autopilot_summary` + `goal-tree.json` → Phase B context_primer 자동 주입

3. EVOLVE 제약:
   - Pipeline mode에서는 goal elevation이 도메인 경계를 넘지 않도록 제한
   - Phase A 내에서만 evolve, 완료 시 Phase B로 핸드오프

## 현재 우회 방법 (임시)

```bash
# 1차 실행
/live "HarnessOS GTM 전략 수립"
# → CONVERGED → episodes.jsonl에 저장

# 2차 실행 (1차 결과 자동 로드됨)
/live "GTM 전략 기반 랜딩 페이지 구현"
# → PRE-LOOP episodes 로드 → 1차 결과 context primer 주입
```

episodes.jsonl이 도메인 간 컨텍스트 브리지 역할 → 반자동 지원.

## 구현 난이도

- MEDIUM: pipeline_goals 파싱 + phase 전환 로직
- DISPATCH 계층에 `pipeline_phase` 상태 변수 추가 필요
- live-state.json에 `pipeline_phase: N` 필드 추가

## 관련 파일

- `/home/jayone/.claude/skills/omc-live/SKILL.md` — Step 3e DISPATCH 계층
- `/home/jayone/.claude/skills/omc-live-inf/SKILL.md` — Step 3e OVERRIDE
