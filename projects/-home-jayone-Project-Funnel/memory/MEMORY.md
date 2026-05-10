# Project Memory

## Development Server Configuration

**Port**: 3004 (항상 사용)
- `npm run dev` → http://localhost:3004
- package.json에 이미 `-p 3004` 설정됨
- 충돌 시: `fuser 3004/tcp` → `kill {PID}`

## Project Structure

- Next.js 16.1.6 (App Router) / TypeScript / Tailwind CSS v3
- **Database: Turso (libSQL/SQLite, 5GB Free)** ← 2026-02-20 Cloudflare D1에서 이전
- Vercel Deployment

## Key Features

1. **Stock Chart**: `/api/stock-prices?symbol=...&days=730` → Turso
2. **Screening**: `/api/screening` → 캐시 우선, 없으면 실시간 fallback (maxDuration=120s) + history 자동 저장
   - 캐시 hit 시에도 `saveScreeningHistory` 호출 (INSERT OR IGNORE → 당일 첫 hit 시만 저장)
   - 결과 테이블: Sector/Cap/누적거래대금/OBV Slope/R²/POC/Near POC/Watch/Match Score
   - 누적 거래대금 = Σ(종가×거래량) 730일, KRW 통일 (미국 ×1350)
3. **Sector Screening**: `/api/sector-screening` + `/api/sector-trends` → 섹터 트렌드 + 낙오주 탐색 (2026-02-24)
4. **Toss Watchlist**: `/api/toss-watchlist` → Playwright headless로 52개 종목 일괄 추가 (maxDuration=300s, 동적 timeout)
5. **Cron Jobs**: 데이터수집 16:00 KST, 스크리닝 분할실행 08:00+08:20 KST (평일만)
   - `?region=korea` (23:00 UTC) → korea만 스크리닝 → cache key='korea'
   - `?region=global` (23:20 UTC) → global 스크리닝 → korea캐시 머지 → cache key='default' + Slack

## Database

**Turso (libSQL)**: `stock-screener-db`
- DB URL: `libsql://stock-screener-db-jaytoone.aws-us-west-2.turso.io`
- DB ID: `58586915-021d-472a-a8ca-f5211684d21f`
- Tables: `stocks` (9,735개, **is_active=1: 9,018개** / is_active=0: 717개 dead US종목), `stock_prices` (2,896,244개 - **2023-10-30 ~ 2026-02-19**, 약 2년 4개월)
- 클라이언트: `src/lib/cloudflare-d1.ts` (파일명 유지, 내부는 @libsql/client 사용)
- 스크리너: `src/lib/screener-d1.ts`

**Supabase** sgmyghfetihejdpxekbr (미사용)
**Cloudflare D1** d7a1d910 (미사용 - 500MB 한도 초과로 이전)

## Turso 핵심 패턴

- 클라이언트 컴포넌트에서 직접 호출 불가 (토큰 노출 위험)
- 반드시 API Route 경유: `ChartContainer → fetch('/api/stock-prices') → Turso`
- 스크리닝: 캐시 hit → 즉시 반환 / 캐시 miss → `screenAllStocksFromDB()` 실시간 수행 + 캐시 저장

## Vercel 환경변수 설정 주의사항

- `vercel env add`로 파이프 시 stdin 전체가 value로 저장되는 버그 있음
- **올바른 방법**: Vercel REST API 사용
  ```bash
  VERCEL_TOKEN=$(cat ~/.local/share/com.vercel.cli/auth.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['token'])")
  curl -X PATCH "https://api.vercel.com/v9/projects/{projectId}/env/{envId}" \
    -H "Authorization: Bearer $VERCEL_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"value": "VALUE", "type": "encrypted"}'
  ```
- project ID: `prj_21wpcrUvuYmsrrAIslPtCyyTwj5J`
- team ID: `team_tUlb8ZnB9UFSTBFbeE6CSHd0`

## Screener 설정 (기본값)

- lookbackDays: 730 / maxMonthlyHighRatio: 0.50
- checkPOC: true / checkValueArea: false
- **2026-02-25 추가**: STS 필터(minSTS), Dollar OBV 필터(minDollarOBV) → ScreenerOptions + UI 적용 예정

## Screener UI 최근 변경 (2026-02-25)

- `formatNumber`: K/M → K/M/B/T 확장 (소수점 1자리)
- `STS 열` 추가: Sector Trend Score = trendStrength×40% + rsVsSpy×30% + return1m×20% + return3m×10%
- `/api/sector-trends` → `sectorTrendMap` 페이지 로드 시 자동 페칭

## stocks.is_active 플래그 (2026-02-21 추가)

- dead 종목 717개 → `is_active=0` (30일 이상 데이터 없는 US 종목)
- Cron/스크리너 쿼리: `WHERE is_active = 1` 필터 적용
- 적용 파일: `update-data/route.ts`, `screener-d1.ts`

## 토스증권 관심종목 자동화 (2026-02-22 최종)

- 스크립트: `scripts/toss-watchlist-add.mjs`
- API: `POST /api/toss-watchlist` → spawn → **항상 headed 브라우저** (세션 파일 없음)
- UI: Screener 페이지에 "Toss 관심종목 추가 (N)" 버튼
- 동작: 브라우저 오픈 → 사용자 로그인 → 자동 추가 (세션 저장 안 함)
- 로그인 감지: **이중 조건** `search_btn 존재 AND login_link 없음` (2026-02-22 DOM 탐침으로 확정)
  - 이유: search_btn은 로그인 전/후 메인 페이지 모두에 표시됨 → 단독 사용 시 오탐
  - login_link(`role=link, name=/로그인/`)는 로그인 전에만 표시됨
  - `/signin` URL 포함 시 체크 스킵
- timeout: `Math.max(symbols.length * 10000, 600000)` (최소 10분)
- 실제 확인된 UI 선택자:
  - 검색 버튼(로그인 감지용): `button /를 눌러 검색하세요/`
  - 검색 입력: `searchbox "검색어를 입력해주세요"`
  - 종목 결과: `role=option` (심볼 정규식 매칭)
  - 종목 URL: `/stocks/{INTERNAL_ID}/order`
  - **팝업 닫기**: 첫 방문 시 `button "닫기"` 클릭 필요
  - 관심종목 버튼: `button /관심 종목/`
  - 그룹 선택: `button[data-contents-code="watchListName"]` 첫 번째 클릭
  - 추가 확인: aria-label에 "해제" 포함 시 성공

## Sector Screening System (2026-02-24 추가)

- **구조**: `src/lib/sector/` (constants, trend, laggard, valuation, fetcher, screener)
- **지표**: RSI(`src/lib/indicators/rsi.ts`), SMA, Mansfield RS
- **DB 신규 테이블**: `stock_fundamentals`, `sector_trends`, `gics_classification`
- **stocks 테이블 확장**: sector, industry, market_cap, cap_category 컬럼 추가
- **데이터 소스**: yahoo-finance2 (quoteSummary) → 섹터/industry/PE/PB/PS/시가총액
- **Sector ETFs**: XLK,XLV,XLF,XLY,XLP,XLI,XLE,XLB,XLC,XLU,XLRE + SPY(벤치마크)
- **설정 완료**: migrate + populate 완료 (8,949/9,008 성공, 27개 필드/종목)
- **stock_fundamentals 필드**: PE, Forward PE, P/B, P/S, PEG, EV/EBITDA, profit/operating margin, ROE, ROA, revenue/earnings growth, beta, dividend yield, MA50/200, analyst target/recommendation, 52w high/low, short ratio, shares/float, avg volume, current price, currency
- **페이지**: `/sector` (Navigation에 탭 추가됨)
- **설계 문서**: `docs/SECTOR_SCREENING_DESIGN.md`

## Sector ETF 가격 수집 (2026-02-25 완료)

- **KIS API ETF 미지원** → yahoo-finance2 `historical()` 사용
- ETF 12개 × 501 records (2024-02-26 ~ 2026-02-24) 수집 완료
- `scripts/backfill-etf-prices.ts`: 초기 730일 백필 (yahoo-finance2)
- `src/app/api/cron/refresh-etf-prices/route.ts`: 일간 갱신 (UTC 08:00, 주말 스킵)
- `src/app/api/cron/refresh-fundamentals/route.ts`: 월간 갱신 (매월 1일 00:00 UTC, batch 1-3)
- `src/lib/sector/fetcher.ts`: yahoo-finance2 v3 `new YahooFinance()` 패턴으로 수정

## 리전 매핑 버그 수정 (2026-02-25)

- **원인**: DB는 `region='KR'`/`'US'`/`'global'` 저장, 쿼리는 `'korea'`/`'global'` 사용 → 0건
- **수정**: `screener-d1.ts` `getAllStocksFromDB()` — `'korea'→KR`, `'global'→IN('US','global')`
- **영향**: Cron의 0-result 캐시 삭제 후 복구 (korea:2,658, global:6,372, all:9,030)

## 미해결 문제

- 없음

## Common Issues

### Weekend Cron Skip
- 주말(토/일)에는 Cron Job이 자동 스킵됨 (정상)

### Stop Hook Playwright 검수 (v2.0.0)
- Flag: `/tmp/pw-verified-{PROJECT}-{SESSION}-{DIFF}.flag`
- 검수 통과 시 hook 지시대로 `touch` 명령어 실행
- 코드 변경 → DIFF_HASH 변경 → 자동으로 새 검수 요구
- 서버 미실행 시 `node_modules/.bin/next dev` 직접 경로 사용 (WSL2 npx 우회)
