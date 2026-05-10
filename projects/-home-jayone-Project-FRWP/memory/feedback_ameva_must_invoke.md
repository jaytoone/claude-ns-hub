---
name: ameva-must-invoke
description: Always invoke ameva via Skill tool when user calls /ameva - never skip even if generic fallback expected
type: feedback
---

/ameva 호출 시 반드시 Skill tool로 정식 실행할 것. "어차피 generic fallback"이라는 판단으로 건너뛰지 말 것.

**Why:** Auto-Corpus Builder가 있어서 코퍼스 미등록 도메인이면 자동 생성됨. generic fallback은 더 이상 존재하지 않음 (first miss → blocking Auto-Corpus Builder). 스킬 실행을 건너뛰면 코퍼스 자동 생성 기회를 놓침.

**How to apply:** `/ameva` 계열 명령어 (/ameva, /ameva -c, /ameva -cr, /ameva -cd, /ameva -crd) 보이면 무조건 Skill tool 먼저 호출. 코퍼스 매칭 여부 판단은 ameva 스킬 내부에서 처리.
