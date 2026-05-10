# Sales Project Memory

## 프로젝트 현황 (2026-04-15)
- Kool: KILLED (4/3) — Jasper/Copy.ai 구조적 경쟁
- CL: KILLED (4/4) — 32건 발송, 10일, reply 0건
- **Conceptual (Arena+Chat)**: 활성 — paintpoint.co.kr/conceptual, v2.3.2
  - Chat: OpenRouter Claude Sonnet 4.6, Arena: Groq 유지
  - v2.3.2: 접이식 "분석 과정" UI (internal_reasoning 노출) — 신뢰 형성 목적, 보안 위험 수용 확정
  - v2.3.1: Arena 가챠 로테이션 + 얼리버드 이메일 수집
  - v2.3.0: Chat 얼리버드 이메일 수집
  - Stage 3 결론 규칙 스킬과 동기화 완료 (자답/되묻기 명시)
- **Conceptual 전략/운영 문서**: `/home/jayone/Project/Moat/docs/conceptual/` 하위에서 관리
- CEO AI Decision Diagnostic 진행 중 (Track A)

## 인프라 (재사용 가능)
- wtp-dashboard: Next.js 16, port 3003, Supabase DB
- wtp_events 테이블: 범용 이벤트 트래킹
- Brevo SMTP 콜드이메일 스크립트
- Fake Door 랜딩 패턴 (pricing → modal → DB)
- LinkedIn Playwright DM 자동화

## 핵심 학습
- LinkedIn DM (12.5% acceptance) >> Cold email (0% reply) in Korea B2B
- 김송희 인터뷰 승인 1건 = LinkedIn이 유일한 action signal 채널
- 김승희: **제외 결정** — 후속 액션 불필요, 언급하지 말 것
- Brevo + paintpoint.co.kr 배달률 69% → 도메인 워밍 필요

## 다음 단계 (2026-04-20 업데이트)
- **4/20 kill 기준 → 연장 결정**: Zoom 인터뷰 2건 예약됨
- **류태섭 Zoom 확정**: 4/23(Thu) 13:00 KST (11:00 → 13:00 reschedule, bidding season conflict), https://us05web.zoom.us/j/83815830479?pwd=aqsEgWeUC0Ivgsfhqpakbiy7tC0Uig.1
- **김근식 Zoom 확정**: 4/22(Wed) 22:00 KST, https://us05web.zoom.us/j/84277114959?pwd=TavGWAtmlbZM6HKGjAhZOJ6WDhCjib.1 (reconfirmed "네 맞습니다")
- 유료 전환 목표: ₩300,000 / 1명 (확장 kill 기준 미정, Zoom 결과 후 재검토)
- 주간 LinkedIn 포스팅: paradigm.json 인사이트 외부화

## 개발 환경
- dev server: `cd wtp-dashboard && npm run dev` (port 3003)
- commit: `git commit -F commit_tree.txt` (Sales 루트에서, 디렉토리명은 WTP 유지)
