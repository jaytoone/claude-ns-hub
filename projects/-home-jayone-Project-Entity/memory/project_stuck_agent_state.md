---
name: stuck_agent_experiment_state
description: Stuck-Agent Escape Rate 실험 현재 상태 — 작업 보류 시점 기록
type: project
---

## 현재 상태 (2026-03-31 보류)

**실험 목표**: 막힌 자율 에이전트의 탈출 전략으로 가설 기반 접근의 유효성 검증 (NeurIPS/ICML 티어)

**완료된 이터레이션**:
- iter 112: analyze.py + test_analyze.py (MINIMAX_API_KEY 반영)
- iter 113: Experiment D framework (passive deceptive tasks) — 71% trivial, dead end
- iter 114: misleading_hint injection — 13 stuck obs, but only 1 discordant pair
- iter 115: ControlledLLMStuckRunner — 40 obs, Eng 97.5% vs Hyp 87.5% (p=0.1336)
- iter 116: 6개 new red_herring tasks (D9-D14) 추가 → 14 tasks / API retry fix

**백그라운드 실험 실행 중**: `b4jttkw36`
- `source ~/.claude/env/shared.env && python3 analyze.py --run-stuck-controlled`
- 14 tasks × 5 trials = 70 obs (controlled, 0 trivial)
- 완료되면 결과 파일: `results/stuck_agent_*.json`

**Why:** 기존 8 tasks (red_herring 2개)에서 discordant pairs=4 (need ≥10). red_herring 카테고리가 가장 강한 신호(-40% hyp penalty) → 8개로 확대

**핵심 발견 (iter 115)**:
- red_herring에서 Engineering 100% vs Hypothesis 60% (-40%)
- semantic_inv에서는 반대로 Hypothesis가 강할 수 있음 (D7: hyp 3/5 wins)
- 전반적으로 p < 0.05 미달, 결과 노이즈 있음

**다음 할 일** (보류 해제 시):
1. `b4jttkw36` 결과 확인 (이미 실행 중)
2. 통계 유의성 확인 (목표: McNemar p < 0.05)
3. 유의성 미달 시 → 전략 재검토:
   - Option A: trials 10으로 증가
   - Option B: semantic_inv 타겟 확대 (hypothesis가 강한 카테고리)
   - Option C: 접근법 전환 — 논문 프레임을 "hypothesis가 더 나음" 대신 "카테고리별 차별화된 효과" 로 재정의

**코드베이스 위치**: `/home/jayone/Project/HarnessOS`
- 실험 코드: `experiments/stuck_agent/`
- 분석 진입점: `analyze.py --run-stuck-controlled`
- 테스트: `tests/test_stuck_agent.py` (52 tests pass)
- 브랜치: `master`, 최근 커밋: `9f09bbd`
