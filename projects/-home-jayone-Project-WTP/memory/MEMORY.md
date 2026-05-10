# Sales Project Memory

## 프로젝트 현황 (2026-04-07)
- Kool: KILLED (4/3) — Jasper/Copy.ai 구조적 경쟁
- CL: KILLED (4/4) — 32건 발송, 10일, reply 0건
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
- Brevo + paintpoint.co.kr 배달률 69% → 도메인 워밍 필요

## 다음 단계
- CEO Diagnostic Batch1: Popup Studio CIO + Nonos CEO InMail 발송 대기
- 4/9: Daejin Park + HeeYoung Hong follow-up
- 유료 전환 목표: ₩300,000 / 1명 (Day 14 = 4/20 kill 기준)
- 주간 LinkedIn 포스팅: paradigm.json 인사이트 외부화

## 개발 환경
- dev server: `cd wtp-dashboard && npm run dev` (port 3003)
- commit: `git commit -F commit_tree.txt` (Sales 루트에서, 디렉토리명은 WTP 유지)
