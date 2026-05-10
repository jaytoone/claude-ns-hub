---
name: DC Posting Lessons
description: DCInside posting constraints learned from first deployment attempt
type: feedback
---

DC HIT 갤러리에 직접 글쓰기 불가능 — HIT는 다른 갤러리에서 추천 받은 글이 자동 수집되는 게시판.
**Why:** HIT 갤러리 baseline 데이터를 수집했지만 직접 포스팅은 마이너갤러리에서만 가능.
**How to apply:** DC 포스팅은 항상 마이너갤러리 (mgallery) 경로 사용. gallery_id=office (직장생활).

DC Playwright 자동 포스팅은 봇 탐지에 걸림 ("올바른 방법으로 이용해 주세요" 오류).
**Why:** DC는 비공식 확장프로그램/자동화 도구를 감지하고 차단.
**How to apply:** DC 포스팅은 수동 복붙으로만 가능. post_browser.py의 DC 부분은 참고용으로만 사용.

"직갤러" 같은 유동닉 기본값은 1인이 아니라 다수 사용자가 동일 닉네임을 공유하는 것.
**Why:** DC 유동닉 기본값 = "{갤러리명}갤러". IP로 구분해야 실제 고유 글쓴이 수 확인 가능.
**How to apply:** 글쓴이 다양성 분석 시 data-nick이 아닌 IP 기반으로 unique count 계산.
