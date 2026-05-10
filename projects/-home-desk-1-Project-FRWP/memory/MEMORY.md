# FRWP Project Memory (desk-1 WSL)

## Current Status (2026-05-06)
- **운영**: WSL2 paper-only mode, hourly cron at :07, Telegram @binancewatch_bot
- **Jetson Xavier** (192.168.0.30): powered OFF — awaiting capital ≥$300
- **Binance balance**: ~$331.90 (above $200 min_balance_floor)
- **Open live positions**: ETH/UNI/SOL/LTC/BAT on exchange-side SL/TP (Xavier off)

## Credentials (saved in .env + shared.env)
- Telegram: @binancewatch_bot (6206784409:AAGbi...) in ~/.claude/channels/telegram/.env
- Turso: frwp-jaytoone.aws-us-west-2.turso.io
- Binance JnQ: OWBUK7Bk... (EXCHANGE_API_KEY/SECRET)
- KIS API: PSl9bq6SZ... (KIS_APP_KEY/KIS_APP_SECRET) — token cached at /tmp/kis_token.txt

## KIS API Findings (2026-05-06 expert-research)
- KR daily 2yr: **FHKST03010100** + `/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice` — date-cursor pagination, 100 rows/call ✅
- KR intraday history: **불가** — FHKST03010200은 당일치만, 역사 분봉 API 없음
- US daily 2yr: HHDFS76240000, BYMD cursor, 100 rows/call ✅
- US intraday: HHDFS76950200, KEYB cursor, depth unconfirmed (likely 30-90d)
- Rate limit: 10 req/s (sleep 0.1s) / Token: 1/min

## Stock Data Collected (data/raw/stock/)
- 1d/: US 20종목 (KIS, 500행 2yr) + KR 14종목 (KIS, 485행 2yr) ✅
- 1h/: US+KR 36종목 (yfinance, 60d) ✅
- 15m/: US+KR 36종목 (yfinance, 60d) ✅
- KR 1h 2yr: yfinance .KS (730d limit) ✅ | KR 15m 2yr: 불가 (무료소스 없음)

## Blood Flow Concept Pivot (2026-05-10)
- Blood flow viz now maps **technological supply chain bottlenecks** → specific stocks
- Bottleneck thesis: OBV accumulating + ST bearish = smart money pre-positioning at chokepoint
- Core bottleneck themes being mapped: AI infra, EV battery chain, grid/power, cybersecurity
- vascular.html (Canvas-based) is the primary viz — port 7788

## Paper Trading (WSL)
- Portfolio: $9,789.34 (dd=2.7%) restored from Turso
- 2-week paper: 18 trades, WR=88.9%, +$87.62
- 2-week live: 15 trades, WR=35.7%, +$5.54 (execution gap known issue)
