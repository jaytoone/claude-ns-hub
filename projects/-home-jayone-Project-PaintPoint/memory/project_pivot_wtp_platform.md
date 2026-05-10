---
name: WTP 검증 플랫폼 피벗
description: PaintPoint deprecate → 멀티서비스 WTP 검증 플랫폼으로 전환 (CL/Kool/future)
type: project
---

PaintPoint 서비스는 deprecated. 플랫폼을 멀티서비스 WTP 검증 플랫폼으로 전환.

**Why:** PaintPoint PMF 미달성. CommentLens(CL)와 Kool이 실제 WTP 검증 타깃.

**How to apply:**
- 신규 기능은 CL/Kool 기준으로 설계
- PP 전용 기능(pp_* 테이블, 이메일 자동화, 보고서) 유지하되 신규 투자 없음
- /live 및 공통 페이지: 서비스별 필터링 구조로 설계
- 향후 서비스 추가 가능한 확장 구조 유지

**아키텍처 방향 (2026-03-28):**
- 공통 페이지: /live (서비스 필터: All | CL | Kool | ...)
- 서비스별 세분화 페이지: /live/cl, /live/kool (향후)
- DB: service 컬럼 기반 통합 뷰 또는 unified outreach 테이블 검토
