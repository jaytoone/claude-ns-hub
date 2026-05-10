---
name: live-inf autonomous — no user prompting between iterations
description: /live-inf does NOT wait for user confirmation between iterations. Continue autonomously until convergence plateau or explicit user stop.
type: feedback
---

`/live-inf` (live 스킬에 `-i` 플래그) 실행 중에는 **iteration 사이에 사용자 지시를 기다리지 않는다**. 이터 1 완료 → 즉시 score → evolve → iter 2 자동 실행. 기본값은 continue, 사용자 선택지를 제시하며 대기하는 것은 spec 위반.

**Why:** live-inf skill 정의("Infinite autonomous self-evolving loop — no iteration budget, context rotation across sessions. Terminates only on convergence plateau or explicit user stop.") — 자율 실행이 핵심 특징. "continue/pause/pivot/stop 선택해주세요" 같은 메뉴는 /live 스킬의 bounded 모드용이지 live-inf 용이 아님.

**How to apply:**
- `/live -i` 또는 `/live-inf` 호출 시: iter N 완료 → 즉시 Score → Evolve 결정 → iter N+1 실행. 사용자 확인 요청 금지.
- 중단 조건: plateau_count >= plateau_k(3) / cumulative_fidelity < 0.50 / context_budget > 70% / 사용자가 명시적으로 "stop"/"cancel"/"멈춰" 입력.
- Score가 YES + delta < epsilon 도 stop이 아니라 같은 goal로 재시도(plateau_count++).
- 사용자 consent gate는 오직 외부 publish(biz-autopilot publish/post/홍보 키워드) 에서만 트리거, 그 외에는 자율.
- 보고는 iter 단위 요약(한 줄)만, "다음 뭐 할까요?" 질문 금지.
