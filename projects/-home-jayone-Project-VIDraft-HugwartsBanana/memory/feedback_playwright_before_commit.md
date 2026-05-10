---
name: playwright-before-commit
description: 구현 완료 후 반드시 Playwright 검수를 먼저 실행하고, 그 다음 커밋 여부를 질문해야 함
type: feedback
---

구현/리팩토링 완료 후 순서: Playwright 검수 → 검수 통과 → 커밋 여부 질문.
커밋 여부를 먼저 묻지 말 것.

**Why:** dev-deep-executor에게 작업을 위임하고 결과를 받은 뒤, TypeScript 체크만 확인하고 바로 커밋 여부를 물었음. Playwright 런타임 검수(탭 클릭, 패널 전환, 콘솔 에러)를 누락했음. stop hook이 이를 감지하여 차단함.

**How to apply:**
- dev-deep-executor/dev-executor 에이전트 프롬프트에 반드시 "Playwright 검수 단계"를 포함시킬 것
- 에이전트가 Playwright 검수를 생략했으면 내가 직접 검수 진행 후 커밋 여부 질문
- 순서: 구현 완료 → TypeScript 체크 → Playwright 검수 → PASS → 커밋 여부 질문
