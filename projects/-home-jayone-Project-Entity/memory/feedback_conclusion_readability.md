---
name: conclusion_readability
description: Entity CONCLUSION uses 세줄결론 (3-line: judgment/evidence/condition) instead of verbose verdict fields
type: feedback
---

Entity 결론이 지표/수치 나열로 시작하면 "그래서 뭐?"가 됨. 세줄결론(판단/근거/조건)으로 구조화.

**Why:** 사용자가 CONCLUSION을 읽고도 "결론이 뭔데?"라는 반응 — 기술적 정보가 결론 역할을 대체하고 있었음

**How to apply:** entity 스킬 응답 시 세줄결론을 반드시 먼저 작성. 1=판단, 2=근거 1문장, 3=뒤집히는 조건 1문장. 3줄 초과 시 QG28 FAIL.
