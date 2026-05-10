# NodeClaw Project Memory

## 세션 2026-03-22 — env 중앙화 완료

### 완료 작업
- `~/.claude/env/shared.env` — 공유 API 키 원본 (Google Cloud, Gemini, YouTube, Tavily, MiniMax, GLM)
- `~/.claude/env/sync.sh / check.sh` — 프로젝트 동기화/검증 스크립트
- `~/.claude/keys/vertex-ai-service-account.json` — GCP SA 키 중앙 이전 (600 권한)
- PaintPoint `.env` `\n` 오염 15개 변수 정리 완료
- `~/.claude/CLAUDE.md` Domain-Specific Guidelines에 공유키 한줄 안내 추가

### 미완료 (NodeClaw 랜딩페이지)
- Google Forms URL 미설정 (`YOUR_GOOGLE_FORMS_URL_HERE`)
- GA4 Measurement ID 미설정 (`YOUR_GA4_MEASUREMENT_ID`)
- GitHub Pages 미배포 — launch-guide.md 참조

### 핵심 문서
- `docs/validation/launch-guide.md` — 30분 배포 체크리스트
- `docs/research/20260322-ai-code-review-market.md` — Claude Code Review $15-25/review 분석
- `~/.claude/env/README.md` — 전체 키 인벤토리
