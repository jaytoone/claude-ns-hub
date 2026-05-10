# PaintPoint Project Memory

## 프로젝트 개요
- YouTube 댓글 페인포인트 분석 서비스
- 경로: `/home/jayone/Project/PaintPoint`
- 대시보드: `painpoint-dashboard/` (Next.js 16 Turbopack + TypeScript + Tailwind)
- 배포: https://paintpoint.co.kr (Vercel Production)
- DB: Supabase PostgreSQL (`pp_` prefix 테이블)

## DB 연결 (v3.41.2 기준 — 중요)
- **Session Pooler** (port 5432): `postgresql://postgres.ekcfgqvtthcjjyjmozuk:cqVUGFqNSYubI97d@aws-1-ap-northeast-2.pooler.supabase.com:5432/postgres`
- DB 클라이언트: `postgres` npm 패키지, `max: 3`, `idle_timeout: 30`
- ⚠️ Transaction Pooler(6543) 사용 금지 — 동시 쿼리 deadlock 이슈 확인됨
- `src/lib/db.ts`: DATABASE_URL에서 `:6543/` → `:5432/` 런타임 교체 로직 포함

## 현재 상태 (v3.41.2, 2026-03-25)
- **v3.41.2**: Supabase Session Pooler 전환 + regions icn1 + chat-stats Promise.all 병렬화
- **v3.41.1**: 대시보드 탭 로딩 속도 개선
  - AdminDashboard lazy mount (초기 API 7→2개)
  - cost-analysis Promise.all 병렬화
  - automation/route.ts strategy_cache JSONB → has_strategy boolean
  - OutreachTab fetch URL credentials 버그 수정 (location.origin)
- **v3.41.0**: CommentLens B2B 아웃리치 대시보드 (cl_outreach 테이블, 트래킹픽셀, 5개 발송)
- **v3.40.x**: 샘플 보고서 데이터 정합성, Hero 컴팩트 개선

## 대시보드 탭 구성 (9개)
`대시보드` | `타깃채널` | `접근IP` | `자동화` | `PMF응답` | `미구독이유` | `API비용` | `채팅` | `아웃리치`

## 주요 API
- `/api/targets/automation` — 자동화 파이프라인 (has_strategy boolean, strategy_cache 제외)
- `/api/cost-analysis` — API 비용 집계 (Promise.all 5쿼리)
- `/api/analytics/chat-stats` — 채팅 통계 (Promise.all 6쿼리)
- `/api/outreach` — B2B 아웃리치 CRUD (cl_outreach 테이블)
- `/api/targets/bulk-resend` — 배치 재발송 (date/none/excludeIds/do_not_contact)

## CommentLens B2B 아웃리치
- `cl_outreach` 테이블: brand/to_email/subject/body_text/sent_at/opened_at/opener_ip/status
- 발송 5건: MANYO FACTORY / ANUA / Beauty of Joseon / TORIDEN / PURITO
- 트래킹 픽셀: `/api/outreach/track-open/[id]`

## 이메일 발송 플로우
```
[대시보드] → /api/targets/[id]/generate-email (Gemini AI 생성)
           → /api/targets/send-email (이미지+추적픽셀 포함)
```
- A/B 테스트 제목 3종 (variantA/B/C) + 열람 추적 픽셀

## API 비용 추적
- 분석: `pp_analysis_sessions` (input/output/thinking_tokens, cost_usd)
- 이메일 생성: `pp_target_channels` (email_gen_cost_usd/input/output_tokens)
- 단가: $0.30/1M input · $2.50/1M output · $2.50/1M thinking
- 누적: ~$3.64 (2026-03 기준)

## Gemini 분석 설정
- 모델: gemini-2.5-flash (thinking 모드)
- AbortController: 200s, Vercel Fluid Compute maxDuration: 300
- 실측: 채널당 평균 $0.12, ~2분 14초

## 미해결 이슈 (우선순위순)
1. **매경 자이앤트 (id=12) 재발송 대기** — mkvodtube@gmail.com, email_sent 상태
2. **Day0 Trial 온보딩 이메일 미구현**
3. **A/B 이메일 variant DB 미저장** — email_subject_variant 컬럼 필요
4. **퍼널 중간 이벤트 추적 없음** — CTA클릭·subscribe도달·checkout열람
5. `/my-report` strategy 섹션 미포함

## TargetStatus 퍼널
`pending` → `email_sent` → `email_opened` → `report_requested` → `survey_done` → `full_report_sent` → `paid` → `rejected`

## Paddle Production
- Basic: `pri_01kjvhx06ndmfxe8j4qf5dq8hp` (KRW 7,900/월, trial 30일)
- Pro: `pri_01kjvj07yk06875464f7kj88vd` (KRW 15,000/월, trial 30일)

## 주요 파일
- `src/components/AdminDashboard.tsx`: lazy mount (탭 첫 클릭시 마운트)
- `src/lib/db.ts`: Session Pooler 전환, max:3
- `src/app/api/analytics/chat-stats/route.ts`: Promise.all 6쿼리 병렬
- `src/app/api/cost-analysis/route.ts`: Promise.all 5쿼리 병렬
- `src/app/api/targets/automation/route.ts`: has_strategy boolean (strategy_cache 제외)
- `src/components/OutreachTab.tsx`: location.origin fetch URL 패턴
- `vercel.json`: regions: ["icn1"], fluid: true

## 개발 환경
- dev server: port 3002 (painpoint-dashboard/ 디렉토리에서 실행)
- commit: `git commit -F commit_tree.txt` (루트에서)
- 문의 이메일: be2jay67@gmail.com
- Basic Auth: admin / paintpoint2026

## UI 규칙
- 이모지 사용 금지, AI 모델명 노출 금지
