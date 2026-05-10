---
name: context efficiency — concise output only
description: Only describe what is necessary. Avoid verbose commit messages, long status reports, redundant explanations.
type: feedback
---

필요한 만큼만 서술. 장황한 커밋 메시지 / 긴 상태 리포트 / 반복 설명 금지.

**Why:** 긴 세션에서 매 턴 컨텍스트가 크게 소비됨. 필수 정보가 아닌 내용은 overhead.

**How to apply:**
- 커밋 메시지: 제목 + 3~5줄 bullet, 부연 설명 제거. iter 요약은 한 줄이면 충분.
- 상태 리포트: 표/bullet 위주, 서술 최소화. 해석·근거·조건 3줄 이상 금지 (세줄결론 스타일).
- 툴 결과에 대한 재서술 금지 — 이미 보이는 출력을 풀어서 반복하지 않음.
- 제안/옵션 열거 시 4개 이상 금지, 기본값 하나만 명시.
- "이제 ~합니다" "다음은 ~입니다" 같은 전환 문구 제거. 바로 본론.
