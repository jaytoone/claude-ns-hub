---
category: SVTool
connections:
- Driller
- FromScratch
current: negative
deadline: ''
layer: 2
log:
- date: '2026-05-11'
  text: 'Blood Flow: Canvas vascular viz + TradingView 3-pane chart (ST+OBV+Slope)
    + mobile opt + tech bottleneck map (9 themes, XYL/ECL/ZS blocked). Chart API :8056.'
- date: '2026-05-11'
  text: 'Blood Flow Scanner: Canvas vascular viz + TradingView chart overlay (ST+OBV
    3-pane) + mobile opt + tech bottleneck mapping (9 themes, XYL/ECL/ZS blocked).
    Chart API port 8056.'
- date: '2026-05-08'
  text: 'ST+OBV 전략 백테스트 완료: US Tier2 avg EV +1.5%, KR avg EV +1.3%. 혈관도 MVE (Dash)
    구현'
- date: '2026-05-07'
  text: 'Phase 3 result: 23/25 symbols negative EV. Only SHIB/SUI (meme/high-vol)
    showed positive. Pattern-based reversal strategies insufficient.'
- date: '2026-05-11'
  text: '71b2a9e pre-format backup: commit all working state; cb30da4 monitor: 3-tier
    sync monitoring (half-hour reconcile + warning telegram + daily report) (+1 more)'
- date: '2026-05-12'
  text: '71b2a9e pre-format backup: commit all working state; cb30da4 monitor: 3-tier
    sync monitoring (half-hour reconcile + warning telegram + daily report) (+1 more)'
metric: Strategy EV after fees (25-symbol avg)
milestones: []
name: FRWP
north_stars:
- current: negative (paper +$87 but sample size small)
  id: crypto_trading
  metric: Live avg monthly return after fees
  milestones:
  - done: true
    text: Paper trading pipeline (WSL + cron + Telegram)
  - done: false
    text: Walk-forward OOS validation ≥30 days
  - done: false
    text: Live dual-mode positive net at $300 capital
  name: FRWP Crypto Strategy
  status: behind
  target: '> 0% (breakeven)'
- current: +1.5% IS avg EV. Bottleneck stocks overlaid on vascular viz.
  id: st_obv_scanner
  metric: OOS walk-forward EV (Tier 2 stocks)
  milestones:
  - done: true
    text: Collect 14K+ stock market data (US+KR, KIS API)
  - done: true
    text: Supertrend + dollar-volume OBV backtest engine
  - done: true
    text: 3-tier volume filter + full universe scan (87K trades)
  - done: true
    text: Bottleneck stocks overlay (9 tech themes mapped to tickers)
  - done: false
    text: Walk-forward OOS validation (2024H1→2024H2)
  - done: false
    text: Live paper trading on top-10 Tier 3 symbols
  name: ST+OBV Stock Scanner
  status: exploring
  target: '> +0.5% per trade OOS'
- current: Canvas viz + TV chart overlay + mobile + bottleneck map. OOS validation
    pending.
  id: blood_flow
  metric: Blockage→breakout accuracy (30d forward)
  milestones:
  - done: true
    text: Blockage score formula + sector aggregation (OBV$ + ST)
  - done: true
    text: Canvas vascular viz (zoom/pan, particles, mobile-responsive)
  - done: true
    text: Sector drilldown + WHY explainability panel
  - done: true
    text: TradingView chart overlay (OHLCV + ST + OBV + Slope + VP)
  - done: true
    text: 'Tech bottleneck mapping (9 themes: HBM/cooling/gases/water/Li/cyber)'
  - done: false
    text: 'Historical backtest: blockage→forward returns validation'
  - done: false
    text: Telegram alert on high-blockage sector detection
  name: Industry Blood Flow Scanner
  status: exploring
  target: '> 60% accuracy'
note: Fixed Risk-Reward Win-ratio Prediction — ML crypto/stock trading strategy
parent: MOAT
position_x: 756
repo_path: ''
status: behind
target: '> 0 (breakeven)'
unit: ''
x: 365
y: 130
---

# FRWP — North Star

## Status (Phase 3 complete)
Pattern-based reversal strategies: 23/25 symbols negative EV. Dead-end.
Pivoting to Phase 4 (new strategy direction needed).