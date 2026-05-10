# Ontolo 프로젝트 현황 (2026-03-06 v1.4 작업 완료)

## 프로젝트 기본 정보
- 경로: `/home/jayone/Project/Ontolo`
- 포트: 3003 (`npm run dev`)
- DB: Supabase (PostgreSQL) - `ekcfgqvtthcjjyjmozuk.supabase.co`
- Prod: https://ontolo.vercel.app

## 현재 상태 (커밋 af2132a)
- **channels/stats 최적화** — 3중 쿼리 → 단일 JOIN 집계 쿼리
- **channels GET 최적화** — SELECT * → 필요 컬럼만 선택 (description 제외)
- **search-query-chat** — 패키지 추가 및 응답 개선
- **Ontolo → Claude Code Sub-Agent 변환 스크립트** 작성 완료
  - DB agents → `~/.claude/agents/*.md` 자동 생성
  - 현재 생성된 에이전트: gap-theory-expert-v3, sales, business-strategy-comprehensive-expert

## 핵심 패턴 (postgres npm 주의사항)
- PostgreSQL NUMERIC/DECIMAL → **문자열로** 반환됨 → `parseFloat()` 필수
- sql 템플릿 리터럴 자동 파라미터화 (SQL Injection 방지)
- Serverless: `max: 1`, `idle_timeout: 20`, `connect_timeout: 10`

## Claude Code Sub-Agent 생성 방법
```bash
PGPASSWORD="..." psql "postgresql://..." \
  -c "COPY (SELECT name, display_name, system_prompt FROM ontolo_agents WHERE status='active') TO STDOUT WITH CSV DELIMITER E'\x01';" \
  > /tmp/ontolo_agents.csv
# python3 스크립트로 ~/.claude/agents/<name>.md 생성
```

## 핵심 파일
- `lib/db.ts` — postgres 직접 연결 클라이언트
- `lib/utils/gemini-client.ts` — Vertex AI createGeminiModel() 유틸
- `app/api/agents/create/route.ts` — MD/JSON 에이전트 생성
- `app/api/channels/route.ts` — 채널 목록 (컬럼 최적화)
- `app/api/channels/stats/route.ts` — 단일 JOIN 집계 쿼리
- `supabase/migrations/` — 6개 마이그레이션 파일

# currentDate
Today's date is 2026-03-06.
